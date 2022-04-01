"""
Entity stats management

"""
from barbarian.utils.rng import Rng, RngDiceError
from barbarian.actions import Action, ActionType
from barbarian.events import Event, EventType
from barbarian.settings import NO_REGEN_HUNGER_STATES


def inflict_damage(action):
    """ Apply damage to hurt actor. """
    actor, target, data = action.unpack()

    assert target.health

    try:
        dmg = Rng.roll_dice_str(data['dmg'])
    except RngDiceError:
        dmg = data['dmg']

    if dmg < 0:
        raise ValueError(
            f"Damage can't be negative (received dmg: {dmg})")

    target.health.hp -= dmg

    if not (msg := data.get('msg', '')):
        msg=f'{actor.name} hits {target.name} for {dmg} hit points!'
    else:
        msg = msg.format(actor=actor, target=target, dmg=dmg)

    action.accept(msg=msg, event_data={'dmg': dmg})

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
    except RngDiceError:
        amount = data['amount']

    pre_heal_hp = target.health.hp
    target.health.hp = min(target.health.hp + amount, target.health.max_hp)

    healed = target.health.hp - pre_heal_hp
    action.accept(msg=f'{target.name} was healed for {healed} hp')


def regenerate(actor, current_tick):
    """ Heal actor by `regen.amount` every `regen.rate` tick. """
    if (regen := actor.regen) is None:
        return

    if actor.health.hp == actor.health.max_hp:
        return

    if ((hunger_clock := actor.hunger_clock) and
        hunger_clock.state in NO_REGEN_HUNGER_STATES
    ):
        return

    if regen.rate > 0 and (current_tick % regen.rate == 0):
        return Action(
            ActionType.HEAL, target=actor, data={'amount': regen.amount})
