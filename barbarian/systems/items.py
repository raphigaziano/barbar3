"""
Item usage logic.

"""
from barbarian.actions import Action


def _get_item(actor, item_id):
    """ Retrieve item by id from actor's inventory. """
    for item in actor.inventory.items:
        if item._id == item_id:
            return item
    raise ValueError(f'Item id {item_id} could not be found.')


def consume_item(actor, item_id):
    """
    Decrement item charges by one and remove it from `actor`'s inventory
    if charges reaches zero.

    No-op is item is not consumable.

    """
    item = _get_item(actor, item_id)
    if item.consumable:
        item.consumable.charges -= 1
        if item.consumable.depleted:
            actor.inventory.items.remove(item)


def use_item(action):
    """ Item usage. """
    actor, _, data = action.unpack()

    item = _get_item(actor, data['item_id'])
    if not item.usable:
        return action.reject(msg=f'Item {item.name} cannot be used')

    new_action_args = item.usable.action
    new_action_args.update(
        item.usable.get_actor_and_target(actor, item))
    action.accept()
    return Action.from_dict(new_action_args)
