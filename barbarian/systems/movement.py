"""
Logic to handle entity movement.

"""
import logging

from barbarian import systems
from barbarian.utils.rng import Rng
from barbarian.actions import Action
from barbarian.events import Event, EventType
from barbarian.components.use import PropActivationMode
from barbarian.utils.structures.dijkstra import DijkstraGrid


logger = logging.getLogger(__name__)


def move_actor(action, level):
    """
    Try moving the actor in the desired direction, and trigger
    any related action or event:

    - Reject the action if destination is blocked
    - Recompute FOV if actor has one
    - Spot actors in visual range
    - Trigger on_enter effects for any props on the destination cell
    - Attack actor on destination cell
    - Trigger on_bump effects for props on the destination tile

    """
    actor, _, data = action.unpack()
    assert hasattr(actor, 'pos')

    (dx, dy) = data['dir']
    # No point in trying to move if the vector is null.
    # This can happen on random direction choice from some ais.
    if (dx, dy) == (0, 0):
        return action.accept()

    destx, desty = actor.pos.x + dx, actor.pos.y + dy
    if not level.map.in_bounds(destx, desty):
        return action.reject()

    if level.move_actor(actor, dx, dy):
        action.accept(
            event_data={'from_x': destx - dx, 'from_y': desty - dy})
        if actor.fov:
            actor.fov.compute(
                level, destx, desty, update_level=actor.is_player)
            spot_entities(actor, level)
        if (prop := level.props[destx, desty]) and (
            prop.trigger and
            prop.trigger.activation_mode == PropActivationMode.ACTOR_ON_TILE
        ):
            return systems.props.trigger(actor, prop)
    else:
        # Technically, the move action has failed, so we should explicitely
        # reject it before returning a new one, in order to emit the fail
        # event which might be needed for commands like autoexplore.
        if target := level.actors[destx, desty]:
            action.reject()
            return Action.attack(actor, target)
        if (prop := level.props[destx, desty]) and (
            prop.trigger and
            prop.trigger.activation_mode == PropActivationMode.ACTOR_BUMP
        ):
            action.reject()
            return systems.props.trigger(actor, prop)

        action.reject(msg=f"{actor.name} can't move here")


def xplore(action, level):
    """
    Compute an exploration map and move the actor one step towards
    the nearest unexplored cell.

    """
    actor = action.actor
    assert hasattr(actor, 'pos')
    if not actor.fov:
        return action.reject(msg=f'{actor} cant xplore: no fov')

    explored_cells = (
        level.explored if actor.is_player else actor.fov.explored)
    dg = DijkstraGrid.new(
        level.map.w, level.map.h,
        *((x, y) for x, y, _ in level.map
          if (x, y) not in explored_cells),
        predicate=lambda x, y, _: (
            (level.props[x,y] is not None and
             level.props[x,y].openable) or
            not level.is_blocked(x, y)
        )
    )

    destx, desty, destc = min(
        dg.get_neighbors(actor.pos.x, actor.pos.y), key=lambda t: t[2])
    if destc == dg.inf:
        action.reject(msg="Can't explore further")
    else:
        action.accept()
        dx, dy = destx - actor.pos.x, desty - actor.pos.y
        return Action.move(actor, d={'dir': (dx, dy)})


_delta_map = {'up': -1, 'down': 1, None: 0}

def change_level(action, world, player, debug=False):
    """
    Move up or down (depending on action data's `dir` key) a
    single level.

    Actual level change is handled by the world object.

    """
    delta = _delta_map[action.data.get('dir')]
    if delta < 0 and world.current_depth == 1:
        return action.reject(msg="You are already on the first level!")

    world.change_level(delta, player, debug)
    action.accept(msg='You enter a new level!')


def spot_entities(actor, level):
    """
    Spot "interesting" entities in visible range.

    For now, this simply emits an event if the spotted entity is deemed
    dangerous. We'll probably add more logic in the future (like an
    actual spot mechanic, ie for trap detection).

    """
    assert actor.fov

    # FIXME: add a "dangerous" component / component prop and just
    # check for it
    for x, y in actor.fov.visible_cells:
        if a := level.actors[x,y]:
            if a is actor:
                continue
            Event.emit(
                EventType.ACTOR_SPOTTED,
                event_data={'actor': actor, 'target': a})
        if p := level.props[x,y]:
            if p.typed.type == 'trap':
                Event.emit(
                    EventType.ACTOR_SPOTTED,
                    event_data={'actor': actor, 'target': p})


def blink(action, level):
    """ Instant move to a random spot in visible range. """
    actor = action.actor

    if not actor.fov:
        return action.reject(msg=f'{actor} cant blink: no fov')

    cells_in_range = list(actor.fov.visible_cells)
    while dest := Rng.choice(cells_in_range):

        dest_x, dest_y = dest
        if actor.pos.distance_from(dest_x, dest_y) <= 1:
            continue

        dx, dy = actor.pos.vector_to(dest_x, dest_y, normalize=False)
        if level.move_actor(actor, dx, dy):
            actor.fov.compute(
                level, actor.pos.x, actor.pos.y, update_level=actor.is_player)
            return action.accept()


def teleport(action, level):
    """ Instant move to a random spot outside visible range. """
    actor = action.actor

    if not actor.fov:
        return action.reject(msg=f'{actor} cant teleport: no fov')

    while dest := Rng.choice([(x, y) for x, y, _ in level.map]):

        dest_x, dest_y = dest
        if (dest_x, dest_y) in actor.fov.visible_cells:
            continue

        dx, dy = actor.pos.vector_to(dest_x, dest_y, normalize=False)
        if level.move_actor(actor, dx, dy):
            actor.fov.compute(
                level, actor.pos.x, actor.pos.y, update_level=actor.is_player)
            return action.accept()
