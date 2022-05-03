from enum import Enum, auto
import logging

from barbarian.utils.rng import Rng
from barbarian.utils.geometry import Rect
from barbarian.genmap.common import BaseMapBuilder
from barbarian.map import TileType


logger = logging.getLogger(__name__)


class SimpleMapBuilder(BaseMapBuilder):
    """ Generic room and corridor, the classic roguebasin algorithm. """

    MAX_ROOMS = 30
    MIN_ROOM_SIZE = 6
    MAX_ROOM_SIZE = 10

    def build(self, depth):
        return self.build_rooms_and_corridors()

    def build_rooms_and_corridors(self):

        for _ in range(self.MAX_ROOMS):

            w = Rng.dungeon.randint(self.MIN_ROOM_SIZE, self.MAX_ROOM_SIZE)
            h = Rng.dungeon.randint(self.MIN_ROOM_SIZE, self.MAX_ROOM_SIZE)
            x = Rng.dungeon.randint(1, self.map.w - w - 2)
            y = Rng.dungeon.randint(1, self.map.h - h - 2)

            new_room = Rect(x, y, w, h)

            ok = True
            for other_room in self.map.rooms:
                if new_room.intersect(other_room):
                    ok = False

            if ok:
                self.take_snapshot(self.map)
                self.apply_room_to_map(self.map, new_room)

                if self.map.rooms:
                    newx, newy = new_room.center
                    prevx, prevy = self.map.rooms[-1].center
                    if Rng.dungeon.randint(0, 1):
                        self.apply_horizontal_tunnel(self.map, prevx, newx, prevy)
                        self.apply_vertical_tunnel(self.map, prevy, newy, newx)
                    else:
                        self.apply_vertical_tunnel(self.map, prevy, newy, prevx)
                        self.apply_horizontal_tunnel(self.map, prevx, newx, newy)

                self.map.rooms.append(new_room)
                self.take_snapshot(self.map)


class BSPMapBuilder(BaseMapBuilder):
    """ A simple BSP dungeon """

    MAX_ROOMS = 240

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rects = []

    def build(self, depth):
        ## Build rooms ##

        self.rects.clear()
        self.rects.append(
            Rect(2, 2, self.map.w - 5, self.map.h - 5))
        first_room = self.rects[0]
        self.add_subrects(first_room)

        n_rooms = 0
        while n_rooms < self.MAX_ROOMS:
            rect = self.get_random_rect()
            candidate = self.get_random_subrect(rect)

            if self.is_possible(candidate):
                self.apply_room_to_map(self.map, candidate)
                self.map.rooms.append(candidate)
                self.add_subrects(rect)
                self.take_snapshot(self.map)

            n_rooms += 1

        ## Build corridors ##
        self.map.rooms.sort(key=lambda r: r.x)  # sort rooms from left to right

        for i in range(len(self.map.rooms)-1):  # ignore last room
            r, next_r = self.map.rooms[i], self.map.rooms[i+1]
            startx = r.x + Rng.dungeon.randint(1, r.w - 1)
            starty = r.y + Rng.dungeon.randint(1, r.h - 1)
            endx = next_r.x + Rng.dungeon.randint(1, next_r.w - 1)
            endy = next_r.y + Rng.dungeon.randint(1, next_r.h - 1)
            self.draw_corridor(startx, starty, endx, endy)
            self.take_snapshot(self.map)

    def add_subrects(self, rect):

        w = abs(rect.x - rect.x2)
        h = abs(rect.y - rect.y2)
        half_w = max(w // 2, 1)
        half_h = max(h // 2, 1)

        self.rects.append(
            Rect(rect.x, rect.y, half_w, half_h ))
        self.rects.append(
            Rect(rect.x, rect.y + half_h, half_w, half_h))
        self.rects.append(
            Rect(rect.x + half_w, rect.y, half_w, half_h))
        self.rects.append(
            Rect(rect.x + half_w, rect.y + half_h, half_w, half_h))

    def get_random_rect(self):
        return Rng.dungeon.choice(self.rects)

    @staticmethod
    def get_random_subrect(rect):
        res = Rect(rect.x, rect.y, rect.w, rect.h)
        rw = abs(rect.x - rect.x2)
        rh = abs(rect.y - rect.y2)

        w = Rng.dungeon.randint(3, max(4, min(rw, 10)))
        h = Rng.dungeon.randint(3, max(4, min(rh, 10)))

        res.x += Rng.dungeon.randint(1, 6) - 1
        res.y += Rng.dungeon.randint(1, 6) - 1
        res.w, res.h = w, h

        return res

    def is_possible(self, rect):
        expanded = Rect(rect.x, rect.y, rect.w, rect.h)
        expanded.x -= 2
        expanded.y -= 2
        expanded.w += 4
        expanded.h += 4

        can_build = True

        for y in range(expanded.y, expanded.y2 + 1):
            for x in range(expanded.x, expanded.x2 + 1):

                if x > self.map.w - 2:  can_build = False
                if y > self.map.h - 2:  can_build = False
                if x < 1:               can_build = False
                if y < 1:               can_build = False
                if can_build:
                    if self.map[x, y] != TileType.WALL:
                        can_build = False

        return can_build

    def draw_corridor(self, startx, starty, endx, endy):
        x, y = startx, starty
        while x != endx or y != endy:
            if x < endx:    x += 1
            elif x > endx:  x -= 1
            elif y < endy:  y += 1
            elif y > endy:  y -= 1

            self.map[x, y] = TileType.FLOOR


class BSPInteriorMapBuilder(BaseMapBuilder):
    """ A simple BSP dungeon """

    MIN_ROOM_SIZE = 8

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rects = []

    def build(self, depth):
        ## Build rooms ##

        self.rects.clear()
        # Start with a single map-sized rect
        self.rects.append(Rect(1, 1, self.map.w - 2, self.map.h - 2))
        first_room = self.rects[0]
        self.add_subrects(first_room)

        rooms = self.rects.copy()
        for r in rooms:
            self.map.rooms.append(Rect(r.x, r.y, r.w - 1, r.h - 1))
            for x in range(r.x, r.x2):
                for y in range(r.y, r.y2):
                    self.map[x,y] = TileType.FLOOR

            self.take_snapshot(self.map)

        for i, room in enumerate(self.map.rooms[:-1]):
            next_room = self.map.rooms[i+1]
            start_x = room.x + (Rng.dungeon.randint(1, room.w) - 1)
            start_y = room.y + (Rng.dungeon.randint(1, room.h) - 1)
            end_x = next_room.x + (Rng.dungeon.randint(1, next_room.w) - 1)
            end_y = next_room.y + (Rng.dungeon.randint(1, next_room.h) - 1)
            self.draw_corridor(start_x, start_y, end_x, end_y)
            self.take_snapshot(self.map)

    def add_subrects(self, rect):
        if self.rects:
            self.rects.pop(-1)

        width = rect.w
        height = rect.h
        half_w = width // 2
        half_h = height // 2

        split = Rng.dungeon.coin_toss()

        if split:
            # Horizontal split
            h1 = Rect(rect.x, rect.y, half_w - 1, height)
            self.rects.append(h1)
            if half_w > self.MIN_ROOM_SIZE:
                self.add_subrects(h1)
            h2 = Rect(rect.x + half_w, rect.y, half_w, height)
            self.rects.append(h2)
            if half_w > self.MIN_ROOM_SIZE:
                self.add_subrects(h2)
        else:
            # Vertical split
            v1 = Rect(rect.x, rect.y, width, half_h - 1)
            self.rects.append(v1)
            if half_h > self.MIN_ROOM_SIZE:
                self.add_subrects(v1)
            v2 = Rect(rect.x, rect.y + half_h, width, half_h)
            self.rects.append(v2)
            if half_h > self.MIN_ROOM_SIZE:
                self.add_subrects(v2)

    def draw_corridor(self, startx, starty, endx, endy):
        x, y = startx, starty
        while x != endx or y != endy:
            if x < endx:    x += 1
            elif x > endx:  x -= 1
            elif y < endy:  y += 1
            elif y > endy:  y -= 1

            self.map[x, y] = TileType.FLOOR


class CellularAutomataMapBuilder(BaseMapBuilder):

    WALL_CHANCE = 55
    SMOOTHING_PASSES = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_pos = None
        self.exit_pos = None

        self.noise_areas = {}

    def build(self, depth):

        # Random walls and floors

        for x, y, _ in self.map:
            if not self.map.in_bounds(x, y, border_width=1):
                continue
            if Rng.dungeon.randint(1, 100) > self.WALL_CHANCE:
                self.map[x,y] = TileType.FLOOR
            else:
                self.map[x,y] = TileType.WALL

        self.take_snapshot(self.map)

        # Apply cellular algotithm

        for _ in range(self.SMOOTHING_PASSES):
            map_copy = self.map.copy()

            for x, y, c in self.map:
                if not self.map.in_bounds(x, y, border_width=1):
                    continue
                wall_neighbors = list(self.map.get_neighbors(
                    x, y, predicate=lambda _, __, c: c == TileType.WALL))

                if not wall_neighbors or len(wall_neighbors) > 4:
                    map_copy[x,y] = TileType.WALL
                else:
                    map_copy[x,y] = TileType.FLOOR

            self.map = map_copy
            self.take_snapshot(self.map)

        # Will be needed for the next step, so let's go ahead
        # and store it to avoid recomputing it later
        self.start_pos = self.get_starting_position()

        # Cull unreachable areas and place the exit as far from the
        # start as possible
        self.exit_pos = self.cull_unreachable_areas(self.start_pos)

        self.take_snapshot(self.map)

        # Create spawn zones
        self.noise_areas = self.generate_voronoi_regions()

    def get_starting_position(self):
        if self.start_pos:
            return self.start_pos
        startx, starty = self.map.w // 2, self.map.h // 2
        while self.map[startx, starty] != TileType.FLOOR:
            startx -= 1
        return startx, starty

    def get_exit_position(self):
        # Was calculated during generation
        return self.exit_pos

    def get_spawn_zones(self):
        return list(self.noise_areas.values())


class DrunkardSpawnMode(Enum):

    STARTING_POINT = auto()
    RANDOM = auto()


class DrunkardWalkBuilder(BaseMapBuilder):

    DEFAULT_DRUNKARD_LIFETIME = 400
    DEFAULT_FLOOR_PERCENTAGE = 50

    def __init__(self,
                 spawn_mode=DrunkardSpawnMode.STARTING_POINT,
                 drunkard_lifetime=None, floor_percentage=None, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.start_pos = None
        self.exit_pos = None

        self.noise_areas = {}
        self.spawn_mode = spawn_mode
        self.drunkard_lifetime = (
            drunkard_lifetime or self.DEFAULT_DRUNKARD_LIFETIME)
        self.floor_percentage = (
            floor_percentage or self.DEFAULT_FLOOR_PERCENTAGE)

    def build(self, depth):

        self.start_pos = self.map.w // 2, self.map.h // 2
        self.map[self.start_pos] = TileType.FLOOR

        desired_floor_cells_count = (
            (self.map.w * self.map.h) * (self.floor_percentage / 100))
        floor_cells_count = len([c for c in self.map.cells if c == TileType.FLOOR])
        digger_count = active_digger_count = 0

        while floor_cells_count < desired_floor_cells_count:

            did_something = False

            if self.spawn_mode is DrunkardSpawnMode.STARTING_POINT:
                drunk_x, drunk_y = self.start_pos
            elif self.spawn_mode is DrunkardSpawnMode.RANDOM:
                if digger_count == 0:
                    drunk_x, drunk_y = self.start_pos
                else:
                    drunk_x = Rng.dungeon.randint(1, self.map.w - 3) + 1
                    drunk_y = Rng.dungeon.randint(1, self.map.h - 3) + 1

            drunk_life = self.drunkard_lifetime

            while drunk_life > 0:

                if self.map[drunk_x, drunk_y] == TileType.WALL:
                    did_something = True
                # TMP value for snapshotting
                self.map[drunk_x, drunk_y] = (
                    TileType.TMP if self.debug else TileType.FLOOR)

                stagger_x, stagger_y = Rng.dungeon.choice(self.map.CARDINAL_DIRS)
                drunk_x = max(2, min(self.map.w - 2, drunk_x + stagger_x))
                drunk_y = max(2, min(self.map.h - 2, drunk_y + stagger_y))

                drunk_life -= 1

            if did_something:
                self.take_snapshot(self.map)
                active_digger_count += 1

            digger_count += 1

            if self.debug:
                # Turn tmp values into floor.
                for x, y, c in self.map:
                    if c == TileType.TMP:
                        self.map[x, y] = TileType.FLOOR

            floor_cells_count = len([c for c in self.map.cells if c == TileType.FLOOR])

        logger.debug(
            "%s dwarves gave up their sobrierty, of whom %s actually found a wall",
            digger_count, active_digger_count)

        self.exit_pos = self.cull_unreachable_areas(self.start_pos)
        self.take_snapshot(self.map)
        self.noise_areas = self.generate_voronoi_regions()

    def get_starting_position(self):
        # Was calculated during generation
        return self.start_pos

    def get_exit_position(self):
        # Was calculated during generation
        return self.exit_pos

    def get_spawn_zones(self):
        return list(self.noise_areas.values())

    # Alternate constructors

    @classmethod
    def open_area(cls, debug=False):
        return cls(debug=debug)

    @classmethod
    def open_halls(cls, debug=False):
        return cls(debug=debug, spawn_mode=DrunkardSpawnMode.RANDOM)

    @classmethod
    def winding_passages(cls, debug=False):
        return cls(
            debug=debug,
            spawn_mode=DrunkardSpawnMode.RANDOM,
            drunkard_lifetime=100,
            floor_percentage=45,
        )
