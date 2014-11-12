# -*- coding: utf8 -*-
"""
barbarian.utils.shapes.py
=========================

Common Shape utilities.

Mostly useful for manipulating the map.

"""

class Rect(object):

    """
    A Simple Rectangular Shape, defined by its top-left corner coordinates,
    width & height.

    """

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @property
    def x2(self):
        return self.x + self.w

    @property
    def y2(self):
        return self.y + self.h

    @property
    def center(self):
        """ Return (x, y) coordinates to this rect's center. """
        center_x = (self.x + self.x2) / 2
        center_y = (self.y + self.y2) / 2
        return (center_x, center_y)

    def intersect(self, other):
        """ Return True if this rectangle intersects with another one. """
        return (self.x <= other.x2 and self.x2 >= other.x and
                self.y <= other.y2 and self.y2 >= other.y)

    # MOAR UTILS
