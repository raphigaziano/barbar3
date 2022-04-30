"""
Prop logic

"""
import logging

from barbarian.actions import Action, ActionType
from barbarian.events import Event, EventType


logger = logging.getLogger(__name__)


def _use_prop(actor, prop, use_component):
    """
    Actual prop use.

    Check charges and return a new action if prop is still charged.

    """
    action = use_component.get_action(actor, prop)
    if prop.consumable:
        if prop.consumable.charges <= 0:
            return None
        event_data = {'entity': prop, 'action': action}
        Event.emit(EventType.ENTITY_CONSUMED, data=event_data)
    return action


def use_prop(action, level):
    """
    Handle a deliberate (ie, initited by an actor, via its ai
    or user input) use of a level prop.

    """
    actor, _, data = action.unpack()

    propx = data.get('propx', actor.pos.x)
    propy = data.get('propy', actor.pos.y)

    if prop := level.props[propx, propy]:
        if prop.usable:
            if (prop.usable.use_key and
                prop.usable.use_key != data['use_key']):
                return action.reject(msg="You can't do that here")
            if (new_action := _use_prop(actor, prop, prop.usable)):
                action.accept()
                return new_action
            return action.reject()
        else:
            logger.warning(
                'Trying to use prop with no use function: %s', prop)

    action.reject(msg="You can't do that here")


def trigger(actor, prop):
    """
    Handle an auto-trigerring prop, whether because an actor has
    entered its cell or because it has bumped into it.

    """
    assert prop.trigger

    if (new_action := _use_prop(actor, prop, prop.trigger)):
        return new_action


def _open_or_close_surrounding_door(action, level):
    """
    Choose a door (or any openable entity) to act upon, based on the
    actor position.

    If action data contains a dx-dy pair, then simply pick the door at
    location (actor_ops + (dx, dy).

    Else, look for candidates on all surrounding tiles.
    If none are found, reject the action.
    If only one is found, pick that canidate and set it at the open/close
    action's target.
    If more than one candidate is found, return a prompt request to
    pick a direction.

    """
    actor, _, data = action.unpack()

    if data and 'dir' in data:
        dx, dy = data['dir']
        px, py = actor.pos.x + dx, actor.pos.y + dy
        if (prop := level.props[px, py]) and prop.openable:
            action.target = prop
            return action
        # Fall back to 'auto' pick below

    should_be_open = action.type == ActionType.CLOSE_DOOR
    surrounding_doors = [
        d for _, __, d in level.props.get_neighbors(
            actor.pos.x, actor.pos.y,
            predicate=lambda _, __, p:
                p is not None and
                p.openable and p.openable.open == should_be_open)
    ]

    if len(surrounding_doors) == 0:
        missing_status = (
            'closed' if action.type == ActionType.CLOSE_DOOR else 'opened')
        return action.reject(
            msg=f'There are no {missing_status} doors around you.')
    elif len(surrounding_doors) == 1:
        action.target = surrounding_doors[0]
        return action
    else:
        return Action.request_input('dir')


def open_or_close_door(action, level):
    """
    Open of close the `target` entity, depending on its current state.

    If `target` is not set, return a modified action via
    `_open_or_close_surrounding_door`.

    """
    actor, door, _ = action.unpack()
    if not door:
        return _open_or_close_surrounding_door(action, level)

    match action.type:

        case ActionType.OPEN_DOOR:

            if door.openable.open:
                return action.reject(msg='Door is already opened')

            door.physics.blocks = False
            door.physics.blocks_sight = False
            door.openable.open = True
            door.usable =  door.usable.new_action({'type': 'close_door'})

        case ActionType.CLOSE_DOOR:

            if not door.openable.open:
                return action.reject(msg='Door is already closed')

            x, y = door.pos.x, door.pos.y
            if level.is_blocked(x, y) or any(level.items[x, y]):
                return action.reject(
                    msg="Can't close door, something is blocking the way")

            door.physics.blocks = True
            door.physics.blocks_sight = True
            door.openable.open = False
            door.usable =  door.usable.new_action({'type': 'open_door'})

        case _:

            return action.reject(
                f'Expected action of type [OPEN|CLOSE]_DOOR, '
                f'got: {action.type}')

    action.accept()

    level.init_fov_map()
    if actor.fov:
        actor.fov.compute(
            level, actor.pos.x, actor.pos.y,
            update_level=actor.is_player)
