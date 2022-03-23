"""
Entity stats management

"""
from barbarian.events import Event, EventType


def inflict_damage(action):
    """ Apply damage to hurt actor. """
    actor, target, data = action.unpack()

    dmg = data['dmg']
    if dmg < 0:
        raise ValueError(
            f"Damage can't be negative (received dmg: {dmg})")
    target.health.hp -= dmg
    action.accept(
        msg=f'{actor.name} hits {target.name} for {dmg} hit points!',
        event_data={'dmg': dmg},
    )

    if target.health.is_dead:
        if target.is_player:
            msg = 'Your dead!'
        else:
            msg = f'{action.target.name} is dead'
        Event.emit(
            EventType.ACTOR_DIED, msg=msg,
            event_data={'actor': target, 'slayer': actor})
