"""
Hunger clock.

"""
from barbarian.utils.rng import Rng
from barbarian.actions import Action
from barbarian.events import Event, EventType
from barbarian.settings import HUNGER_DMG_CHANCE, HUNGER_DMG


def tick(actor, current_tick):
    """
    Update hunger clock, triggering an event on state change.

    Also take care of potential static effects related to the
    current hunger state (ie, taking damage when starving.

    """
    if not (clock := actor.hunger_clock):
        return

    pre_tick_state = clock.state

    if clock.rate > 0 and (current_tick % clock.rate == 0):
        clock.satiation -= 1

        if clock.state != pre_tick_state:
            msg = f'{actor.name} is {clock.state}'
            Event.emit(
                EventType.FOOD_STATE_UPDATED,
                msg=msg, event_data={'actor': actor, 'state': clock.state})

    if clock.starving:
        if Rng.randint(0, 100) < HUNGER_DMG_CHANCE:
            dmg_data = {
                'dmg': HUNGER_DMG, 'msg': '{target.name} suffers {dmg} damage'}
            return Action.inflict_dmg(None, actor, dmg_data)
