# -*- coding: utf8 -*-
"""
Common geometric utilities.

Mostly useful for manipulating the map.

"""
import math


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


# Stolen from https://github.com/encukou/bresenham
def bresenham(x0, y0, x1, y1):
    """
    Yield integer coordinates on the line from (x0, y0) to (x1, y1).
    Input coordinates should be integers.
    The result will contain both the start and the end point.


    """
    dx = x1 - x0
    dy = y1 - y0

    xsign = 1 if dx > 0 else -1
    ysign = 1 if dy > 0 else -1

    dx = abs(dx)
    dy = abs(dy)

    if dx > dy:
        xx, xy, yx, yy = xsign, 0, 0, ysign
    else:
        dx, dy = dy, dx
        xx, xy, yx, yy = 0, ysign, xsign, 0

    distance = 2*dy - dx
    y = 0

    for x in range(dx + 1):
        yield x0 + x*xx + y*yx, y0 + x*xy + y*yy
        if distance >= 0:
            y += 1
            distance-= 2*dx
        distance += 2*dy


def distance_from(from_x, from_y, to_x, to_y):
    """
    Return the distance between the entity and a point located
    at (x, y)

    """
    return int(math.sqrt((to_x - from_x) ** 2 + (to_y - from_y) ** 2))


def vector_to(from_x, from_y, target_x, target_y, normalize=True):
    """
    Return a vector pointing to position (target_x, target_y).

    If param `normalize` is True, then the vector will be reduced to
    len(1).

    """
    dx, dy = target_x - from_x, target_y - from_y

    if not normalize:
        return dx, dy

    vx = vy = 0

    if dx > 0:      vx = 1
    elif dx < 0:    vx = -1

    if dy > 0:      vy = 1
    elif dy < 0:    vy = -1

    return vx, vy
