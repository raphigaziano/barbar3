from barbarian.utils.rng import Rng
from barbarian.map import Map, TileType


class BaseMapBuilder:
    """
    Base class for map builders, implementing the basic building
    process as well as some common actions.

    """

    def __init__(self, debug=False):
        self.debug = debug
        self.map = None
        self.snapshots = []

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
