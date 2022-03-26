"""
Item handling logic.

"""
from barbarian.components.physics import Position


def get_item(action, level):
    """
    Get items (single or all) lying on the tile `actor` is standing on.

    """
    actor, _, data = action.unpack()

    assert actor.inventory

    if not level.items[actor.pos.x, actor.pos.y]:
        return action.reject(msg='No items here')

    # We do not care (yet?) about actual ordering (which is why we use
    # python's object id as a key), we just want to ensure consistent
    # display.
    for item in sorted(level.items[actor.pos.x, actor.pos.y], key=id):
        level.items.remove_e(item)
        item.remove_component('pos')
        actor.inventory.items.append(item)

    action.accept(msg='Picked up all the items')


def drop_item(action, level):
    """
    Drop items (single or all) from `actor`'s inventory and add them
    back to the level map.

    """
    actor, _, data = action.unpack()

    assert actor.inventory

    if not actor.inventory.items:
        return action.reject(msg="Nothing to drop")

    while actor.inventory.items:
        item = actor.inventory.items.pop()
        item.add_component('pos', Position(actor.pos.x, actor.pos.y))
        level.items.add_e(item)

    action.accept(msg='Dropped all the items')
