# -*- coding: utf8 -*-
"""
barbarian.map.py
================

Basic Map data structure.

"""
from barbarian import libtcodpy as libtcod


class OutOfBoundGridError(IndexError, Exception):
    """
    Moar explicit IndexError.

    Raised when trying to access a non existing cell.

    """
    pass


class Grid(object):

    """ Generic 2D Matrix container """

    def __init__(self, width, height, cells=None):
        self.w = width
        self.h = height
        self.cells = cells or []

    def get_cell(self, x, y):
        """ Get the cell at cartesian coordinates (x, y). """
        try:
            return self.cells[self._cartesian_to_idx(x, y)]
        except IndexError:
            raise OutOfBoundGridError(
                "Can't access cell %d-%d: Out of bounds" % (x, y)
            )

    def __getitem__(self, pos):
        """ Shortcut for Grid.get_cell. """
        # TODO: moar doc
        if isinstance(pos, slice):
            msg = ('Slicing is not allowed on %(cls)s. Use the explicit '
                   '%(cls)s.slice method instead' % {'cls': self.__class__})
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
        """ Return a sub-grid object, which rect is defined by x, y, w & h. """
        cells = [
            self.cells[self._cartesian_to_idx(_x, _y)]
            for _y in range(y, y+h) for _x in range(x, x+w)
        ]
        return self.__class__(w, h, cells)

    def slice_from_rect(self, rect):
        """ Helper to slice directly from a Rect object. """
        return self.slice(rect.x, rect.y, rect.w, rect.h)

    ### Alternate constructors ###
    ##############################

    @classmethod
    def from_grid(cls, grid, cell_converter=None):
        # This might be useless, but i can see it being handy to build grids or
        # even a final map from other temporary grids
        if cell_converter is not None:
            cells = map(cell_converter, grid.cells)
        else:
            cells = grid.cells

        return cls(grid.w, grid.h, cells)

    ### Internal Utils ###
    ######################

    # Do we *really* gain anything from storing the cells in a continuous array ?

    def _idx_to_cartesian(self, idx):
        """ Convert internal array index to cartesian coordinates. """
        return idx % self.w, idx / self.w

    def _cartesian_to_idx(self, x, y):
        """ Convert cartesian coordinates to internal array index. """
        return x + (y * self.w)


class Map(Grid):

    """ Basic Map object """

    def __init__(self, width, height, cells=None):
        super(Map, self).__init__(width, height, cells)
        self.fov_map = libtcod.map_new(self.w, self.h)

    def init_fov_map(self):
        """
        Initialize the fov map.

        Make sure to call it *AFTER* cells have been populated.

        """
        for x, y, cell in iter(self):
            libtcod.map_set_properties(
                self.fov_map, x, y, not cell.blocks_sight, not cell.blocks
            )

    def compute_fov(self, from_x, from_y):
        """
        Recompute fov based on the (from_x, from_y) position.

        (Typically, (from_x, from_y) will be the player's current position).

        """
        libtcod.map_compute_fov(
            self.fov_map, from_x, from_y, 10, True, 0   # TODO: use constants
        )
        for x, y, cell in iter(self):
            if self.is_in_fov(x, y):
                cell.explored = True

    def is_in_fov(self, x, y):
        """
        Return whether map pos (x, y) is in fov.

        Shortcut for calling libtcod.map_is_in_fov(map, x, y)

        """
        return libtcod.map_is_in_fov(self.fov_map, x, y)

    def is_obj_in_fov(self, obj):
        """
        Return whether map obj is in fov.

        Shortcut for calling libtcod.map_is_in_fov(map, obj.x, obj.y)

        """
        return self.is_in_fov(obj.x, obj.y)
