"""
Hunger clock.

"""
from barbarian.utils.rng import Rng
from barbarian.actions import Action
from barbarian.events import Event, EventType
from barbarian.settings import MAX_HUNGER_SATIATION, HUNGER_DMG_CHANCE, HUNGER_DMG


def _update_hunger_clock(actor, delta):
    """
    Actual food clock update logic, used both by eat action and tick system. 

    """
    if not (clock := actor.hunger_clock):
        return

    pre_update_state = clock.state
    clock.satiation = min(MAX_HUNGER_SATIATION, (clock.satiation + delta))
    if clock.state != pre_update_state:
        msg = f'{actor.name} is {clock.state}'
        Event.emit(
            EventType.FOOD_STATE_UPDATED,
            msg=msg, event_data={'actor': actor, 'state': clock.state})


def eat(action):
    """ Consume food item if actor is not full. """

    actor, target, _ = action.unpack()

    assert actor.hunger_clock and target.edible

    if actor.hunger_clock.full:
        return action.reject(msg=f"{actor.name}'s stomach is already full")

    action.accept(msg='Yum!')
    _update_hunger_clock(actor, target.edible.nutrition)


def tick(actor, current_tick):
    """
    Update hunger clock, triggering an event on state change.

    Also take care of potential static effects related to the
    current hunger state (ie, taking damage when starving.

    """
    if not (clock := actor.hunger_clock):
        return

    if clock.rate > 0 and (current_tick % clock.rate == 0):
        _update_hunger_clock(actor, -1)

    if clock.starving:
        if Rng.randint(0, 100) < HUNGER_DMG_CHANCE:
            dmg_data = {
                'dmg': HUNGER_DMG, 'msg': '{target.name} suffers {dmg} damage'}
            return Action.inflict_dmg(None, actor, dmg_data)
