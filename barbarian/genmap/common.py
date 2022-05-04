from enum import Enum, auto

from barbarian.utils.rng import Rng
from barbarian.utils.structures.dijkstra import DijkstraGrid
from barbarian.utils.noise import get_cellular_voronoi_noise_generator
from barbarian.map import Map, TileType


class Symmetry(Enum):
    NONE = auto()
    HORIZONTAL = auto()
    VERTICAL = auto()
    BOTH = auto()


class BaseMapBuilder:
    """
    Base class for map builders, implementing the basic building
    process as well as some common actions.

    """
    DEFAULT_BRUSH_SIZE = 1
    DEFAULT_SYMMETRY = Symmetry.NONE

    def __init__(
        self, debug=False,
        brush_size=DEFAULT_BRUSH_SIZE, symmetry=DEFAULT_SYMMETRY
    ):
        self.debug = debug
        self.map = None
        self.snapshots = []

        self.brush_size = brush_size
        self.symmetry = symmetry

    def take_snapshot(self, m):
        """
        Store a copy of the current map state for debugging.

        No-op if the the map's debug flag is False.

        """
        if self.debug:
            self.snapshots.append(m.copy())

    @staticmethod
    def apply_room_to_map(m, room):
        for y in range(room.y, room.y2 + 1):
            for x in range(room.x, room.x2 + 1):
                m[x, y] = TileType.FLOOR

    @staticmethod
    def apply_horizontal_tunnel(m, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if m.in_bounds(x, y):
                m[x, y] = TileType.FLOOR

    @staticmethod
    def apply_vertical_tunnel(m, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if m.in_bounds(x, y):
                m[x, y] = TileType.FLOOR

    def cull_unreachable_areas(self, start_pos):
        """
        Turn any unreachable cell to a wall, and return the position
        most distant from (start_x, start_y).

        """
        cur_dist = 0
        exit_pos = (0, 0)
        dg = DijkstraGrid.new(
            self.map.w, self.map.h, start_pos,
            predicate=lambda x, y, _: self.map[x,y] != TileType.WALL)

        for x, y, dist_to_start in dg:
            if self.map.cell_blocks(x, y):
                continue
            if dist_to_start == dg.inf:
                # Can't reach (x,y), so make it a wall
                self.map[x, y] = TileType.WALL
            elif dist_to_start > cur_dist:
                # Push exit further and further from the start
                exit_pos = (x, y)
                cur_dist = dist_to_start

        return exit_pos

    def generate_voronoi_regions(self):

        noise_areas = {}
        noise = get_cellular_voronoi_noise_generator(Rng.dungeon)
        for x, y, c in self.map:
            if not self.map.in_bounds(x, y, border_width=1):
                continue
            if c == TileType.FLOOR:
                fnoise_val = noise.get_noise(float(x), float(y))
                noise_val = int(fnoise_val * 10240.0)
                noise_areas.setdefault(noise_val, []).append((x, y))

        return noise_areas

    def paint(self, x, y, tile_type=TileType.FLOOR):

        match self.symmetry:

            case Symmetry.NONE:
                self._apply_paint(x, y, tile_type)

            case Symmetry.HORIZONTAL:
                center_x = self.map.w // 2
                if x == center_x:
                    self._apply_paint(x, y, tile_type)
                else:
                    dist_x = abs(center_x - x)
                    self._apply_paint(center_x + dist_x, y, tile_type)
                    self._apply_paint(center_x - dist_x, y, tile_type)

            case Symmetry.VERTICAL:
                center_y = self.map.h // 2
                if y == center_y:
                    self._apply_paint(x, y, tile_type)
                else:
                    dist_y = abs(center_y - y)
                    self._apply_paint(x, center_y + dist_y, tile_type)
                    self._apply_paint(x, center_y - dist_y, tile_type)

            case Symmetry.BOTH:
                center_x = self.map.w // 2
                center_y = self.map.h // 2
                if x == center_x and y == center_y:
                    self._apply_paint(x, y, tile_type)
                else:
                    dist_x = abs(center_x - x)
                    dist_y = abs(center_y - y)
                    self._apply_paint(
                        center_x + dist_x, center_y + dist_y, tile_type)
                    self._apply_paint(
                        center_x - dist_x, center_y - dist_y, tile_type)
                    self._apply_paint(
                        center_x - dist_x, center_y + dist_y, tile_type)
                    self._apply_paint(
                        center_x + dist_x, center_y - dist_y, tile_type)

    def _apply_paint(self, x, y, tile_type):
        if self.brush_size == 1:
            self.map[x, y] = tile_type
        else:
            half_brush_size = self.brush_size // 2
            for brush_x in range(x-half_brush_size, x+half_brush_size):
                for brush_y in range(y - half_brush_size, y + half_brush_size):
                    if (
                        1 <= brush_x < self.map.w - 1 and
                        1 <= brush_y < self.map.h - 1
                    ):
                        self.map[brush_x, brush_y] = tile_type

    def get_starting_position(self):
        return self.map.rooms[0].center

    def get_exit_position(self):
        return self.map.rooms[-1].center

    def get_spawn_zones(self):
        # Assumes map has rooms.
        tiles = []
        for rect in self.map.rooms:
            rtiles = []
            for x in range(rect.x, rect.x2 + 1):
                for y in range(rect.y, rect.y2 + 1):
                    rtiles.append((x, y))
            tiles.append(rtiles)
        return tiles

    def build_map(self, w, h, depth):
        self.map = Map(w, h, [TileType.WALL for _ in range(w * h)])
        self.build(depth)
        return self.map

    def build(self, dpeth):
        raise NotImplementedError()
