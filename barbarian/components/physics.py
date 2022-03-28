"""
Simple data components to represent the basics of an object
like position, physicality and an internal representation.

Almost all game entities will probably own one of those.

"""
from barbarian.components.base import Component


class Position(Component):

    __attr_name__ = 'pos'
    __serialize__ = True

    x: int
    y: int

    def serialize(self):
        return [self.x, self.y]


class Solid(Component):

    __attr_name__ = 'physics'

    blocks: bool = True
    blocks_sight: bool = False
