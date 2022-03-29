"""
Item usage logic.

"""
from barbarian.actions import Action
from barbarian.events import Event, EventType


def _get_item(actor, item_id):
    """ Retrieve item by id from actor's inventory. """
    for item in actor.inventory.items:
        if item._id == item_id:
            return item
    raise ValueError(f'Item id {item_id} could not be found.')


def use_item(action):
    """ Item usage. """
    actor, _, data = action.unpack()

    item = _get_item(actor, data['item_id'])
    if not item.usable:
        return action.reject(msg=f'Item {item.name} cannot be used')

    if item.consumable:
        event_data = {'entity': item, 'owner': actor}
        Event.emit(EventType.ENTITY_CONSUMED, data=event_data)

    action.accept()

    return item.usable.get_action(actor, item)
