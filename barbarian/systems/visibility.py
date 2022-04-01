"""
Routines to spot stuff (ie detect if some specific entity is in fov).

"""
from barbarian.events import Event, EventType


def spot_player(actor, player):
    """
    Can `actor` see the player ?

    Try and use the actor's own fov, and falls back to a simple
    'if the player can see me, then I can see him' check if actor has
    no fov.

    """
    if actor.fov:
        return (player.pos.x, player.pos.y) in actor.fov.visible_cells
    return player.fov.is_in_fov(actor.pos.x, actor.pos.y)


def spot_entities(actor, level):
    """
    Spot "interesting" entities in visible range.

    For now, this simply emits an event if the spotted entity is deemed
    dangerous. We'll probably add more logic in the future (like an
    actual spot mechanic, ie for trap detection).

    """
    if not actor.fov:
        return

    # FIXME: add a "dangerous" component / component prop and just
    # check for it
    for x, y in actor.fov.visible_cells:
        if a := level.actors[x,y]:
            if a is actor:
                continue
            Event.emit(
                EventType.ACTOR_SPOTTED,
                event_data={'spotter': actor, 'spotted': a})
        if p := level.props[x,y]:
            if p.typed.type == 'trap' and not p.consumable.depleted:
                Event.emit(
                    EventType.ACTOR_SPOTTED,
                    event_data={'spotter': actor, 'spotted': p})
