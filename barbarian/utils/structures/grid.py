"""
Useful data structures.

"""
import itertools


class GridError(Exception):
    pass


class OutOfBoundGridError(IndexError, GridError):
    """
    Moar explicit IndexError.

    Raised when trying to access a non existing cell.

    """
    def __init__(self, x, y, msg=""):
        if not msg:
            msg = f"Can't access cell {x}-{y}: Out of bounds"
        super().__init__(msg)


class Grid:
    """ Generic 2D Matrix container """

    __slot__ = ('cells',)

    CARDINAL_DIRS = (
        (0, -1), (1, 0), (0, 1), (-1, 0))       # N, E, S, W
    DIAGONAL_DIRS = (
        (1, -1), (1, 1), (-1, 1), (-1, -1))     # NE, SE, SW, NW
    ALL_DIRS =  CARDINAL_DIRS + DIAGONAL_DIRS

    def __init__(self, width, height, cells=None):
        self.w = width
        self.h = height
        if cells is not None and len(cells):
            if len(cells) != self.w * self.h:
                raise GridError(
                    f'Invalid cell list size. '
                    f'Grid of size ({self.w}, {self.h} should contain '
                    f'{self.w * self.h} cells. Passed list contains {len(cells)}')
            self.cells = cells
        else:
            self.cells = [None] * (self.w * self.h)

    def in_bounds(self, x, y):
        """ Check that (x, y) is in the grid. """
        return 0 <= x < self.w and 0 <= y < self.h

    def get_cell(self, x, y):
        """ Get the cell at cartesian coordinates (x, y). """
        if not (0 <= x < self.w and 0 <= y < self.h):
        # if not self.in_bounds(x, y):
            raise OutOfBoundGridError(x, y)
        return self.cells[x + (y * self.w)]

    def set_cell(self, x, y, v):
        """ Set the cell at cartesian coordinates (x, y). """
        if not (0 <= x < self.w and 0 <= y < self.h):
        # if not self.in_bounds(x, y):
            raise OutOfBoundGridError(x, y)
        self.cells[x + (y * self.w)] = v

    def _pos_to_xy(self, pos):
        # TODO: moar doc
        if isinstance(pos, slice):
            cls = self.__class__
            msg = (
                f'Slicing is not allowed on {cls}. Use the explicit '
                '{cls}.slice method instead')
            raise TypeError(msg)

        try:
            x, y = pos
        except (TypeError, ValueError) as e:
            cls = self.__class__
            msg = (
                'Custom indexing for {cls} objects. '
                'Use obj[x,y] (both values are mandatory).')
            raise IndexError(msg) from e

        return x, y

    def __getitem__(self, pos):
        """ Shortcut for Grid.get_cell. """
        x, y = self._pos_to_xy(pos)
        return self.get_cell(x, y)

    def __setitem__(self, pos, v):
        """ Shortcut for Grid.set_cell. """
        x, y = self._pos_to_xy(pos)
        self.set_cell(x, y, v)

    def get_neighbors(self, x, y, cardinal_only=False, predicate=None):
        """
        Return all cells surrounding the target cell, as (x, y, c) tuples
        like when iterating over the whole map.

        Out of bounds cells will be silently ignored.

        """
        dirs = (
            self.CARDINAL_DIRS if cardinal_only else self.ALL_DIRS)

        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            try:
                c = self.get_cell(nx, ny)
                if predicate and not predicate(nx, ny, c):
                    continue
                yield nx, ny, c
            except OutOfBoundGridError:
                # This will cause a "incomplete" list to be returned, which may
                # or may not be whet the calling code expects.
                pass

    def __iter__(self):
        """
        Iterator implentation.

        return 3 tuples of (x_position, y_postion, cell_object).

        """
        for i, c in enumerate(self.cells):
            x, y = i % self.w, i // self.w
            yield x, y, c
         # ~ raise StopIteration

    def copy(self):
        return self.__class__(self.w, self.h, self.cells[:])

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

    def merge_grid(self, x, y, subgrid):
        # TODO: TEST!
        # ERR CHECK!
        # Name ????
        for sub_x, sub_y, c in subgrid:
            cell_i = self._cartesian_to_idx(x + sub_x, y + sub_y)
            self.cells[cell_i] = c

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
        return idx % self.w, idx // self.w

    def _cartesian_to_idx(self, x, y):
        """ Convert cartesian coordinates to internal array index. """
        return x + (y * self.w)


class EntityGrid(Grid):
    """
    Store arbitrary objects on a 2D grid.

    """
    def __init__(self, width, height):
        cells = [None for _ in range(width * height)]
        Grid.__init__(self, width, height, cells)

    def __iter__(self):
        for x, y, obj in super().__iter__():
            if obj is not None:
                yield x, y, obj

    def __len__(self):
        return len(self.all)

    @property
    def all(self):
        return [e for _, __, e in self]

    def add(self, x, y, obj):
        self.set_cell(x, y, obj)

    def remove(self, x, y, _):
        self.set_cell(x, y, None)

    def add_e(self, e):
        """
        Assume the passed object (entity) stores its position
        on a subobject named `pos`, and add it to the grid.

        """
        self.add(e.pos.x, e.pos.y, e)

    def remove_e(self, e):
        """
        Assume the passed object (entity) stores its position
        on a subobject named `pos` and remove it to the grid.

        """
        self.remove(e.pos.x, e.pos.y, e)


class GridContainer(EntityGrid):
    """
    Specialized EntityGrid storing groups of objects on a single
    cell.

    Each cell will be a set containing the stored objects for this position.

    """

    def __init__(self, width, height):
        cells = [set() for _ in range(width * height)]
        Grid.__init__(self, width, height, cells)

    def __iter__(self):
        for x, y, obj_list in super().__iter__():
            for o in obj_list:
                yield x, y, o

    @property
    def all(self):
        return list(itertools.chain.from_iterable(self.cells))

    def add(self, x, y, obj):
        self.get_cell(x, y).add(obj)

    def remove(self, x, y, obj):
        self.get_cell(x, y).remove(obj)
