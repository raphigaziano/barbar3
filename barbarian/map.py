# -*- coding: utf8 -*-
"""
barbarian.map.py
================

Basic Map data structure.

"""


class OutOfBoundMapError(IndexError, Exception):
    """
    Moar explicit IndexError.

    Raised when trying to access a non existing cell.

    """
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

    def __getitem__(self, pos):
        """ Shortcut for Map.get_cell. """

        # TODO: moar doc
        if isinstance(pos, slice):
            msg = ('Slicing is not allowed on %s. Use the explicit '
                   '%s.slice method instead' % (self.__class__, self.__class__))
            raise TypeError(msg)

        try:
            x, y = pos
        except (TypeError, ValueError):
            msg = ('Custom indexing for %s objects. '
                   'Use obj[x,y] (both values are mandatory).' % self.__class__)
            raise IndexError(msg)

        return self.get_cell(x, y)

    def __iter__(self):
        """
        Iterator implentation.

        return 3 tuples of (x_position, y_postion, cell_object).

        """
        for i, c in enumerate(self.cells):
            x, y = self._idx_to_cartesian(i)
            yield x, y, c
        raise StopIteration

    def slice(self, x, y, w, h):
        """ Return a submap object, which rect is defined by x, y, w & h. """
        cells = []
        for _x, _y, c in self:
            if _x >= x and _x < (x + w) and _y >= y and _y < (y + h):
                cells.append(c)
        return self.__class__(w, h, cells)

    def slice_from_rect(self, rect):
        return self.slice(rect.x, rect.y, rect.w, rect.h)

    ### Internal Utils ###
    ######################

    def _idx_to_cartesian(self, idx):
        """ Convert internal array index to cartesian coordinates. """
        return idx % self.w, idx / self.w

    def _cartesian_to_idx(self, x, y):
        """ Convert cartesian coordinates to internal array index. """
        return x + (y * self.w)
