"""
Item handling logic.

"""
from barbarian.components.physics import Position


def get_item(action, level):

    actor, _, data = action.unpack()

    assert actor.inventory

    if not level.items[actor.pos.x, actor.pos.y]:
        return action.reject(msg='No items here')

    for item in sorted(level.items[actor.pos.x, actor.pos.y], key=id):
        level.items.remove_e(item)
        item.remove_component('pos')
        actor.inventory.items.append(item)

    action.accept(msg='Picked up all the items')


def drop_item(action, level):

    actor, _, data = action.unpack()

    assert actor.inventory

    if not actor.inventory.items:
        return action.reject(msg="Nothing to drop")

    while actor.inventory.items:
        item = actor.inventory.items.pop()
        item.add_component('pos', Position(actor.pos.x, actor.pos.y))
        level.items.add_e(item)

    action.accept(msg='Dropped all the items')
