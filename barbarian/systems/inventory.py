"""
Inventory handling logic.

"""
from barbarian.components.physics import Position


def _select_items(action_data, item_list):
    """
    Filter `item_list`.

    If action_data contains a `item_id_list` iterable, then any items which
    an id not in said list will be excluded.
    Otherwise, all items are returned.

    Note: the id used for filtering is the barbarian's entity _id field, 
    *not* python's object id.

    """
    data = action_data or {}
    if item_id_list := data.get('item_id_list', []):
        return [item for item in item_list if item._id in item_id_list]
    else:
        return item_list


def _get_item(actor, item, level):
    """ Get a single item from the level. """
    level.items.remove_e(item)
    item.remove_component('pos')
    actor.inventory.items.append(item)
    return item


def _drop_item(actor, item, level):
    """ Drop a single item from actor's inventory. """
    actor.inventory.items.remove(item)
    item.add_component('pos', Position(actor.pos.x, actor.pos.y))
    level.items.add_e(item)
    return item


def get_items(action, level):
    """
    Get items (single or all) lying on the tile `actor` is standing on.

    """
    actor, _, data = action.unpack()

    assert actor.inventory

    if not level.items[actor.pos.x, actor.pos.y]:
        return action.reject(msg='No items here')

    items = _select_items(data, level.items[actor.pos.x, actor.pos.y])
    processed = []

    # We do not care (yet?) about actual ordering (which is why we use
    # python's object id as a key), we just want to ensure consistent
    # display.
    for item in sorted(items, key=id):
        processed.append(_get_item(actor, item, level))

    picked_up_str = ', '.join(i.name for i in processed)
    action.accept(msg=f'Picked up: {picked_up_str}')


def drop_items(action, level):
    """
    Drop items (single or all) from `actor`'s inventory and add them
    back to the level map.

    """
    actor, _, data = action.unpack()

    assert actor.inventory

    if not actor.inventory.items:
        return action.reject(msg="Nothing to drop")

    items = _select_items(data, actor.inventory.items)
    processed = []

    # Sorting is even less usefull here, but do it anyway to be consistent.
    for item in sorted(items, key=id):
        processed.append(_drop_item(actor, item, level))

    droped_str = ', '.join(i.name for i in processed)
    action.accept(msg=f'Dropped: {droped_str}')
