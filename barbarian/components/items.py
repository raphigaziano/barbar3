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

    items: list = field(default_factory=list)
