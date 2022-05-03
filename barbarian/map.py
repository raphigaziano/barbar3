"""
Sepcialized grid to hold map data.

"""
from enum import Enum
import logging

from barbarian.utils.structures.grid import Grid, OutOfBoundGridError


logger = logging.getLogger(__name__)


class TileType(Enum):
    """ Type for a map cell. """
    TMP = 'X'
    FLOOR = '.'
    WALL = '#'


class Map(Grid):
    """ Specialized Grid to represent map of a game level. """

    BLOCKING_TILE_TYPES = (
        TileType.WALL,
    )

    def __init__(self, *args, **kwargs):
        self.rooms = []
        self.regions = []

        self.bitmask_grid = None

        super().__init__(*args, **kwargs)

    def in_bounds(self, x, y, border_width=0):
        """
        Return whether (x, y) falls outside the map's bounds.
        Border size will shrink the valid area, which can be useful
        to exclude the edges of the map or restrict the check to a
        smaller area.

        """
        return (
            border_width <= x < self.w - border_width and
            border_width <= y < self.h - border_width)

    def cell_blocks(self, x, y):
        """
        Return whether the passed in cell should block movement.

        This only check map tiles and ignores entity that may
        occupy the cell (This check is the Level's job).

        """
        return self.get_cell(x, y) in self.BLOCKING_TILE_TYPES

    def compute_bitmask_grid(self):
        """ Build a bitmask grid of the map cells. Used for rendering. """
        self.bitmask_grid = Grid(self.w, self.h)
        for x, y, _ in self:
            self.bitmask_grid[x,y] = self.get_bitmask(x, y)

    def get_bitmask(self, x, y):
        """ Compute a specific cell's bitmask. """
        # if x < 1 or x > self.w-2 or y < 1 or y > self.h-2:
        #     return 35

        def _is_room_border(x, y):
            def is_wall(x, y):
                try:
                    return self[x, y] == TileType.WALL
                except OutOfBoundGridError:
                    return True

            return (is_wall(x,y) and any((
                not is_wall(nx, ny) for nx, ny, _ in self.get_neighbors(x, y)
            )))

        mask = 0

        if _is_room_border(x, y - 1): mask += 1
        if _is_room_border(x, y + 1): mask += 2
        if _is_room_border(x - 1, y): mask += 4
        if _is_room_border(x + 1, y): mask += 8

        return mask

    def _floodfill(self, x, y, predicate, action=None):
        # TODO: TESTS!!
        # TODO: recursive (this version) or stack based (private version below) ?
        cell = self[x, y]
        if predicate(cell):
            if action is not None:
                action(cell)
            yield cell
            self.floodfill(x + 1, y, predicate, action) # right
            self.floodfill(x - 1, y, predicate, action) # left
            self.floodfill(x, y + 1, predicate, action) # down
            self.floodfill(x, y - 1, predicate, action) # up

    def floodfill(self, x, y, predicate, action=None):
        """
        Yield all reacheable (accordingt to `predicate`) cells, starting
        from (x, y).

        Option `action` should be a callable wich will be run for each
        yielded cell.

        REFACT: pass more arguments (like the cell itself, maybe the map ?)
        to both the predicate and action callables.

        """
        stack = set()
        visited = set()
        stack.add( (x, y) )
        while len(stack) > 0:
            x, y = stack.pop()
            if self.in_bounds(x, y):
                continue
            if (x, y) in visited:
                continue

            visited.add((x, y))
            cell = self[x, y]
            if not predicate(cell):
                continue
            if action is not None:
                action(cell)

            stack.add( (x + 1, y) )  # right
            stack.add( (x - 1, y) )  # left
            stack.add( (x, y + 1) )  # down
            stack.add( (x, y - 1) )  # up

            yield cell

    def serialize(self):
        return {
            'width': self.w,
            'height': self.h,
            'cells': [c.value for c in self.cells],
            'bitmask_grid':
                self.bitmask_grid.cells if self.bitmask_grid else None,
        }
