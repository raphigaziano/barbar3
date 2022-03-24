# -*- coding: utf8 -*-
"""
Common geometric utilities.

Mostly useful for manipulating the map.

"""


class Rect:
    """
    A Simple Rectangular Shape, defined by its top-left corner coordinates,
    width & height.

    """

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def __repr__(self):
        return f'Rect(x={self.x}, y={self.y}, w={self.w}, h={self.h})'

    @property
    def x2(self):
        return self.x + self.w

    @property
    def y2(self):
        return self.y + self.h

    @property
    def center(self):
        """ Return (x, y) coordinates to this rect's center. """
        center_x = (self.x + self.x2) // 2
        center_y = (self.y + self.y2) // 2
        return (center_x, center_y)

    def intersect(self, other):
        """ Return True if this rectangle intersects with another one. """
        return (self.x <= other.x2 and self.x2 >= other.x and
                self.y <= other.y2 and self.y2 >= other.y)


class Circle:

    """
    A circular shape, defined by it's center coordinates and radius.

    """

    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.r = radius

    @property
    def center(self):
        return self.x, self.y

    def intersect(self, other):
        pass

    def get_inner_coords(self):
        for x in range(self.x - self.r - 1, self.x + self.r):
            for y in range(self.y - self.r - 1, self.y + self.r):
                if (
                    (x-self.x)*(x-self.x) + (y-self.y)*(y-self.y) <
                    self.r * self.r + self.r
                ):
                    yield x, y
