# -*- coding: utf8 -*-
"""
barbarian.map.py
================

Basic Map data structure.

"""


class OutOfBoundMapError(IndexError, Exception):
    pass

class Map(object):

    """ Basic Map object """

    def __init__(self, width, height, cells=None):
        self.w = width
        self.h = height
        self.cells = cells or []

    def get_cell(self, x, y):
        """ Get the cell at cartesian coordinates (x, y). """
        try:
            return self.cells[self._cartesian_to_idx(x, y)]
        except IndexError:
            raise OutOfBoundMapError(
                "Can't access cell %d-%d: Out of bounds" % (x, y)
            )

    def __iter__(self):
        """
        Iterator implentation.

        return a 3 tuple of (x_position, y_postion, cell object).

        """
        for i, c in enumerate(self.cells):
            x, y = self._idx_to_cartesian(i)
            yield x, y, c
        raise StopIteration

    def slice(self, x, y, w, h):
        """ Return a submap object, which rect is defined by x, y, w & h. """
        # Dummy stub.
        cells = [0, 0, 0]
        return self.__class__(w, h, cells)

    ### Internal Utils ###
    ######################

    def _idx_to_cartesian(self, idx):
        """ Convert internal array index to cartesian coordinates. """
        return idx % self.w, idx / self.w

    def _cartesian_to_idx(self, x, y):
        """ Convert cartesian coordinates to internal array index. """
        return x + (y * self.w)
