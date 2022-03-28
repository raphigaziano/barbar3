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


def use_item(action):
    """ Item usage. """
    actor, _, data = action.unpack()

    item = _get_item(actor, data['item_id'])
    if not item.usable:
        return action.reject(msg=f'Item {item.name} cannot be used')

    # FIXME: this should be handled elsewhere, to avoid consuming the
    # item if its action is rejected...
    if item.consumable:
        item.consumable.charges -= 1
        if item.consumable.depleted:
            actor.inventory.items.remove(item)

    new_action_args = item.usable.action
    new_action_args.update(
        item.usable.get_actor_and_target(actor, item))
    action.accept()
    return Action.from_dict(new_action_args)
