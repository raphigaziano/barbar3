"""
Item management components.

"""
from dataclasses import field

from barbarian.components.base import Component


class Item(Component):
    """
    Flag component.

    An item can be picked up or dropped, and can be stored in an inventory.

    """
    __flyweight__ = True


class Inventory(Component):

    __slots = (
        'weapon', 'shield',
        'armor', 'helmet', 'boots', 'gloves',
        # 'ring_1', 'ring_2', 'amulet'
    )

    items: list = field(default_factory=list)

    def __post_init__(self):
        self.slots = {k: None for k in self.__slots}

    def serialize(self):
        return {
            'items': [i.serialize() for i in self.items],
            'slots': {
                slot_name:
                    slot_item.serialize() if slot_item is not None else None
                for slot_name, slot_item in self.slots.items()
            }
        }


class Equipable(Component):
    __flyweight__ = True
    __serialize__ = True

    inventory_slot: str
