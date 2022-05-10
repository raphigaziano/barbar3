"""
Field of view computing

"""
from dataclasses import dataclass

from barbarian.utils.structures.grid import Grid, OutOfBoundGridError
from barbarian.utils.geometry import bresenham


@dataclass
class FovCell:
    """
    Fov map cell.

    Store transparency status and whether or not this location was in fov range
    for the last computation.

    """
    blocks_sight: bool
    in_fov: bool = False


class FovMap(Grid):

    """ Visibility Map. """

    def __init__(self, width, height):
        super().__init__(
            width, height,
            cells=[FovCell(True) for _ in range(width * height)])

    def set_cell(self, x, y, blocks_sight):
        """ Set transparency for a single cell. """
        if not (0 <= x < self.w and 0 <= y < self.h):
            raise OutOfBoundGridError(x, y)
        self.cells[x + (y * self.w)].blocks_sight = blocks_sight

    def set_all_cells(self, cell_cb):
        """
        Set all transparency for all cells to the value returned by
       `cell_cb`.

        Callback should accept x and y arguments and return True or False.

        """
        for x, y, _ in self:
            self.set_cell(x, y, cell_cb(x, y))

    def get_processed_area(self, from_x, from_y, radius):
        """
        Return a square area centered on (from_x, from_y) with the given radius.

        """
        x_min = 0
        y_min = 0
        x_max = self.w
        y_max = self.h
        if radius > 0:
            x_min = max(x_min, from_x - radius)
            y_min = max(y_min, from_y - radius)
            x_max = max(x_max, from_x + radius + 1)
            y_max = max(y_max, from_y + radius + 1)
        return x_min, y_min, x_max, y_max

    # Algorithm lifted from tcod:
    # https://github.com/libtcod/libtcod/blob/develop/src/libtcod/fov_circular_raycasting.c
    def compute(self, from_x, from_y, radius, light_walls):

        """ Compute visibility for all cells in range """

        if not (0 <= from_x < self.w and 0 <= from_y < self.h):
            raise OutOfBoundGridError(from_x, from_y)

        # Clear map: no cell is visible
        for c in self.cells:
            c.in_fov = False

        x_min, y_min, x_max, y_max = self.get_processed_area(from_x, from_y, radius)

        # Start position  is visible
        self.cells[from_x + (from_y * self.w)].in_fov = True

        # Cast rays along the perimeter.
        radius_squared = radius * radius
        for x in range(x_min, x_max):
            self.cast_ray(
                from_x, from_y, x, y_min, radius_squared, light_walls)
        for y in range(y_min + 1, y_max):
            self.cast_ray(
                from_x, from_y, x_max - 1, y, radius_squared, light_walls)
        for x in range(x_max - 2, x_min - 1, -1):
            self.cast_ray(
                from_x, from_y, x, y_max - 1, radius_squared, light_walls)
        for y in range(y_max - 2, y_min - 1, -1):
            self.cast_ray(
                from_x, from_y, x_min, y, radius_squared, light_walls)

        if light_walls:
            self.postprocess(from_x, from_y, radius)

    def cast_ray(self, start_x, start_y, end_x, end_y, radius_squared, light_walls):
        """
        Cast a ray to the given target position and mark each cell across it
        as being is fov.

        Abort when we hit a wall or exceed the range.

        """
        for x, y in bresenham(start_x, start_y, end_x, end_y):

            if not (0 <= x < self.w and 0 <= y < self.h):
                return      # Out of bounds

            if radius_squared > 0:
                distance_from_start = (
                    (x - start_x) * (x - start_x) +
                    (y - start_y) * (y - start_y))
                if distance_from_start > radius_squared:
                    return  # Out of range

            cell_idx = x + (y * self.w)

            if self.cells[cell_idx].blocks_sight:
                if light_walls:
                    self.cells[cell_idx].in_fov = True
                return      # Blocked by wall

            self.cells[cell_idx].in_fov = True

    def postprocess(self, from_x, from_y, radius):

        """ Spread light along walls to avoid lightingh artifacts. """

        x_min, y_min, x_max, y_max = self.get_processed_area(from_x, from_y, radius)

        # North-West quadrant
        self._postprocess_quadrant(
            x_min, y_min, from_x, from_y, -1, -1)
        # South-West quadrant
        self._postprocess_quadrant(
            from_x, y_min, x_max - 1, from_y, 1, -1)
        # North-East quadrant
        self._postprocess_quadrant(
            x_min, from_y, from_x, y_max - 1, -1, 1)
        # South-East quadrant
        self._postprocess_quadrant(
            from_x, from_y, x_max - 1, y_max - 1, 1, 1)

    def _postprocess_quadrant(self, x0, y0, x1, y1, dx, dy):
        """
        Postprocess a specific quadrant, spreading light along the
        (dx, dy) vector.

        """
        if abs(dx) != 1 or abs(dy) != 1:
            return

        n_cells = self.w * self.h

        for cx in range(x0, x1 + 1):
            for cy in range(y0, y1 + 1):
                cell_idx = cx + (cy * self.w)
                # Floor tile in fov
                if (
                    cell_idx < n_cells and
                    self.cells[cell_idx].in_fov and
                    not self.cells[cell_idx].blocks_sight
                ):
                    nx = cx + dx
                    ny = cy + dy
                    # dx neighbor
                    if x0 <= nx <= x1:
                        n_idx = nx + (cy * self.w)
                        if n_idx < n_cells and self.cells[n_idx].blocks_sight:
                            self.cells[n_idx].in_fov = True
                    # dy neighbor
                    if y0 <= ny <= y1:
                        n_idx = cx + (ny * self.w)
                        if n_idx < n_cells and self.cells[n_idx].blocks_sight:
                            self.cells[n_idx].in_fov = True
                    # dx-dy neighbor
                    if x0 <= nx <= x1 and y0 <= ny <= y1:
                        n_idx = nx + (ny * self.w)
                        if n_idx < n_cells and self.cells[n_idx].blocks_sight:
                            self.cells[n_idx].in_fov = True
