"""
Entity stats management

"""
from barbarian.utils.rng import Rng, DiceError
from barbarian.events import Event, EventType


def inflict_damage(action):
    """ Apply damage to hurt actor. """
    actor, target, data = action.unpack()

    assert target.health

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
            msg = f'{target.name} is dead'
        Event.emit(
            EventType.ACTOR_DIED, msg=msg,
            event_data={'actor': target, 'slayer': actor})


def heal(action):
    """ Heal targeted actor. """
    _, target, data = action.unpack()

    assert target.health

    if target.health.hp == target.health.max_hp:
        return action.reject(msg=f'{target.name} is already at max health')

    try:
        amount = Rng.roll_dice_str(data['amount'])
    except DiceError:
        amount = data['amount']

    pre_heal_hp = target.health.hp
    target.health.hp = min(target.health.hp + amount, target.health.max_hp)

    healed = target.health.hp - pre_heal_hp
    action.accept(msg=f'{target.name} was healed for {healed} hp')
