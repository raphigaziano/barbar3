"""
Simple data components to represent the basics of an object
like position, physicality and an internal representation.

Almost all game entities will probably own one of those.

"""
import math

from barbarian.components.base import Component


class Position(Component):

    __attr_name__ = 'pos'
    __serialize__ = True

    x: int
    y: int

    def distance_from(self, x, y):
        """
        Return the distance between the entity and a point located
        at (x, y)

        """
        return int(math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2))

    def vector_to(self, target_x, target_y, normalize=True):
        """ Return a normalized vector pointing to position (target_x, target_y) """
        dx, dy = target_x - self.x, target_y - self.y

        if not normalize:
            return dx, dy

        vx = vy = 0

        if dx > 0:      vx = 1
        elif dx < 0:    vx = -1

        if dy > 0:      vy = 1
        elif dy < 0:    vy = -1

        return vx, vy

    def serialize(self):
        return [self.x, self.y]


class Solid(Component):

    __attr_name__ = 'physics'

    blocks: bool = True
    blocks_sight: bool = False
