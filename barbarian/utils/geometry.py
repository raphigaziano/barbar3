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
        self.x1 = x
        self.y1 = y
        self.x2 = self.x1 + w
        self.y2 = self.y1 + h
        # ???
        self.w = w
        self.h = h

    def center(self):
        """ Return (x, y) coordinates to this rect's center. """
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)

    def intersect(self, other):
        """ Return True if this rectangle intersects with another one. """
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

    # MOAR UTILS
