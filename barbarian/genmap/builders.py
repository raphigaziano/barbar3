from enum import Enum, auto
import logging

from barbarian.utils.rng import Rng
from barbarian.utils.geometry import Rect, bresenham
from barbarian.utils.structures.grid import Grid
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
        self.take_snapshot(self.map)

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
                digger_x, digger_y = self.start_pos
            elif self.spawn_mode is DrunkardSpawnMode.RANDOM:
                if digger_count == 0:
                    digger_x, digger_y = self.start_pos
                else:
                    digger_x = Rng.dungeon.randint(1, self.map.w - 3) + 1
                    digger_y = Rng.dungeon.randint(1, self.map.h - 3) + 1

            drunk_life = self.drunkard_lifetime

            while drunk_life > 0:

                if self.map[digger_x, digger_y] == TileType.WALL:
                    did_something = True
                # TMP value for snapshotting
                self.map[digger_x, digger_y] = (
                    TileType.TMP if self.debug else TileType.FLOOR)

                stagger_x, stagger_y = Rng.dungeon.choice(self.map.CARDINAL_DIRS)
                digger_x = max(2, min(self.map.w - 2, digger_x + stagger_x))
                digger_y = max(2, min(self.map.h - 2, digger_y + stagger_y))

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


class MazeMapBuilder(BaseMapBuilder):

    SNAPSHOT_FREQUENCY = 25

    class MazeCell:

        def __init__(self, x, y):
            self.x, self.y = x, y
            self.walls = {
                'TOP': True, 'RIGHT': True, 'BOTTOM': True, 'LEFT': True}
            self.visited = False

        def remove_walls(self, other_cell):
            x = self.x - other_cell.x
            y = self.y - other_cell.y

            if x == 1:
                self.walls['LEFT'] = False
                other_cell.walls['RIGHT'] = False
            elif x == -1:
                self.walls['RIGHT'] = False
                other_cell.walls['LEFT'] = False
            elif y == 1:
                self.walls['TOP'] = False
                other_cell.walls['BOTTOM'] = False
            elif y == -1:
                self.walls['BOTTOM'] = False
                other_cell.walls['TOP'] = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_pos = None
        self.exit_pos = None

        self.noise_areas = {}

    def build(self, depth):

        maze = Grid((self.map.w // 2) - 2, (self.map.h // 2) - 2)
        self.generate_maze(maze)

        self.start_pos = self.get_starting_position()
        self.take_snapshot(self.map)
        self.exit_pos = self.cull_unreachable_areas(self.start_pos)
        self.take_snapshot(self.map)

        # Create spawn zones
        self.noise_areas = self.generate_voronoi_regions()

    def generate_maze(self, maze_grid):

        for x, y, _ in maze_grid:
            maze_grid[x, y] = self.MazeCell(x, y)

        current = (0, 0)
        backtrace = []

        i = 0
        while True:
            cur_cell = maze_grid[current]
            cur_cell.visited = True
            next_ = self.find_next_cell(current, maze_grid)

            if next_:
                next_x, next_y, next_cell = next_
                backtrace.append((next_x, next_y))

                cur_cell.remove_walls(next_cell)
                current = (next_x, next_y)
            else:
                if backtrace:
                    current = backtrace.pop(0)
                else:
                    break

            if self.debug and i % self.SNAPSHOT_FREQUENCY == 0:
                self.update_map(maze_grid)
                self.take_snapshot(self.map)
            i += 1

        self.update_map(maze_grid)

    def find_next_cell(self, current_cell, maze_grid):
        neighbors = list(maze_grid.get_neighbors(
            *current_cell, cardinal_only=True,
            predicate=lambda _, __, c: not c.visited
        ))
        if neighbors:
            return Rng.dungeon.choice(neighbors)
        return None

    def update_map(self, maze_grid):

        for maze_x, maze_y, maze_cell in maze_grid:

            map_x, map_y = (maze_x + 1) * 2, (maze_y + 1) * 2
            self.map[map_x, map_y] = TileType.FLOOR
            if not maze_cell.walls['TOP']:
                self.map[map_x, map_y - 1] = TileType.FLOOR
            if not maze_cell.walls['RIGHT']:
                self.map[map_x + 1, map_y] = TileType.FLOOR
            if not maze_cell.walls['BOTTOM']:
                self.map[map_x, map_y + 1] = TileType.FLOOR
            if not maze_cell.walls['LEFT']:
                self.map[map_x - 1, map_y] = TileType.FLOOR

    def get_starting_position(self):
        startx, starty = self.map.w // 2, self.map.h // 2
        while self.map[startx, starty] != TileType.FLOOR:
            startx -= 1
        return startx, starty

    def get_exit_position(self):
        # Was calculated during generation
        return self.exit_pos

    def get_spawn_zones(self):
        return list(self.noise_areas.values())


class DLAAlgorithm(Enum):
    WALK_INWARDS = auto()
    WALK_OUTWARDS = auto()
    CENTRAL_ATTRACTOR = auto()


class DLASymmetry(Enum):
    NONE = auto()
    HORIZONTAL = auto()
    VERTICAL = auto()
    BOTH = auto()


class DLAMapBuilder(BaseMapBuilder):

    DEFAULT_ALGORITHM = DLAAlgorithm.WALK_INWARDS
    DEFAULT_BRUSH_SIZE = 1
    DEFAULT_SYMMETRY = DLASymmetry.NONE
    DEFAULT_FLOOR_PERCENTAGE = 30

    def __init__(
            self, algorithm=None, brush_size=None, symmetry=None, floor_percentage=None,
            *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.start_pos = None
        self.exit_pos = None

        self.noise_areas = {}

        self.algorithm = algorithm or self.DEFAULT_ALGORITHM
        self.brush_size = brush_size or self.DEFAULT_BRUSH_SIZE
        self.symmetry = symmetry or self.DEFAULT_SYMMETRY
        self.floor_percentage = floor_percentage or self.DEFAULT_FLOOR_PERCENTAGE

    def build(self, depth):

        # Dig a starting "seed" area
        start_x, start_y = self.map.w // 2, self.map.h // 2
        self.start_pos = start_x, start_y
        self.take_snapshot(self.map)

        self.map[self.start_pos] = TileType.FLOOR
        self.map[start_x + 1, start_y] = TileType.FLOOR
        self.map[start_x - 1, start_y] = TileType.FLOOR
        self.map[start_x, start_y + 1] = TileType.FLOOR
        self.map[start_x, start_y - 1] = TileType.FLOOR
        self.take_snapshot(self.map)

        desired_floor_cells_count = (
            (self.map.w * self.map.h) * (self.floor_percentage / 100))
        floor_cells_count = len([c for c in self.map.cells if c == TileType.FLOOR])

        while floor_cells_count < desired_floor_cells_count:

            # Works, but painfully slow :(
            if self.algorithm == DLAAlgorithm.WALK_INWARDS:

                digger_x = Rng.dungeon.randint(1, self.map.w - 3) + 1
                digger_y = Rng.dungeon.randint(1, self.map.h - 3) + 1
                prev_x, prev_y = digger_x, digger_y
                while self.map[digger_x, digger_y] == TileType.WALL:
                    prev_x, prev_y = digger_x, digger_y
                    stagger_x, stagger_y = Rng.dungeon.choice(self.map.CARDINAL_DIRS)
                    digger_x = max(
                        2, min(self.map.w - 2, digger_x + stagger_x))
                    digger_y = max(
                        2, min(self.map.h - 2, digger_y + stagger_y))
                self.paint(prev_x, prev_y)

            # This doesn't work right.
            # Confirmed at https://github.com/amethyst/rustrogueliketutorial/issues/129
            # but no fix yet.
            elif self.algorithm == DLAAlgorithm.WALK_OUTWARDS:

                digger_x, digger_y = self.start_pos
                while self.map[digger_x, digger_y] == TileType.FLOOR:
                    stagger_x, stagger_y = Rng.dungeon.choice(self.map.CARDINAL_DIRS)
                    digger_x = max(
                        2, min(self.map.w - 2, digger_x + stagger_x))
                    digger_y = max(
                        2, min(self.map.h - 2, digger_y + stagger_y))
                self.paint(digger_x, digger_y)

            elif self.algorithm == DLAAlgorithm.CENTRAL_ATTRACTOR:

                start_pos_x, start_pos_y = self.start_pos
                digger_x = Rng.dungeon.randint(1, self.map.w - 3) + 1
                digger_y = Rng.dungeon.randint(1, self.map.h - 3) + 1
                prev_x, prev_y = digger_x, digger_y

                path_to_center = bresenham(
                    digger_x, digger_y, start_pos_x, start_pos_y)

                for px, py in path_to_center:
                    if self.map[px, py] != TileType.WALL:
                        break
                    prev_x, prev_y = px, py

                self.paint(prev_x, prev_y)

            self.take_snapshot(self.map)
            floor_cells_count = len([c for c in self.map.cells if c == TileType.FLOOR])

        self.exit_pos = self.cull_unreachable_areas(self.start_pos)
        self.take_snapshot(self.map)
        self.noise_areas = self.generate_voronoi_regions()

    def paint(self, x, y):

        match self.symmetry:

            case DLASymmetry.NONE:
                self.apply_paint(x, y)

            case DLASymmetry.HORIZONTAL:
                center_x = self.map.w // 2
                if x == center_x:
                    self.apply_paint(x, y)
                else:
                    dist_x = abs(center_x - x)
                    self.apply_paint(center_x + dist_x, y)
                    self.apply_paint(center_x - dist_x, y)

            case DLASymmetry.VERTICAL:
                center_y = self.map.h // 2
                if y == center_y:
                    self.apply_paint(x, y)
                else:
                    dist_y = abs(center_y - y)
                    self.apply_paint(x, center_y + dist_y)
                    self.apply_paint(x, center_y - dist_y)

            case DLASymmetry.BOTH:
                center_x = self.map.w // 2
                center_y = self.map.h // 2
                if x == center_x and y == center_y:
                    self.apply_paint(x, y)
                else:
                    dist_x = abs(center_x - x)
                    dist_y = abs(center_y - y)
                    self.apply_paint(center_x + dist_x, center_y + dist_y)
                    self.apply_paint(center_x - dist_x, center_y - dist_y)
                    self.apply_paint(center_x - dist_x, center_y + dist_y)
                    self.apply_paint(center_x + dist_x, center_y - dist_y)

    def apply_paint(self, x, y):
        if self.brush_size == 1:
            self.map[x, y] = TileType.FLOOR
        else:
            half_brush_size = self.brush_size // 2
            for brush_x in range(x-half_brush_size, x+half_brush_size):
                for brush_y in range(y - half_brush_size, y + half_brush_size):
                    if (
                        1 <= brush_x < self.map.w - 1 and
                        1 <= brush_y < self.map.h - 1
                    ):
                        self.map[brush_x, brush_y] = TileType.FLOOR

    def get_starting_position(self):
        # Was calculated during generation
        return self.start_pos

    def get_exit_position(self):
        # Was calculated during generation
        return self.exit_pos

    def get_spawn_zones(self):
        return list(self.noise_areas.values())

    @classmethod
    def walk_inwards(cls, debug=False):
        return cls(
            debug=debug,
            algorithm=DLAAlgorithm.WALK_INWARDS,
            brush_size=1,
            symmetry=DLASymmetry.NONE)

    @classmethod
    def walk_outwards(cls, debug=False):
        return cls(
            debug=debug,
            algorithm=DLAAlgorithm.WALK_OUTWARDS,
            brush_size=2,
            symmetry=DLASymmetry.NONE)

    @classmethod
    def central_attractor(cls, debug=False):
        return cls(
            debug=debug,
            algorithm=DLAAlgorithm.CENTRAL_ATTRACTOR,
            brush_size=2,
            symmetry=DLASymmetry.NONE)

    @classmethod
    def insectoid(cls, debug=False):
        return cls(
            debug=debug,
            algorithm=DLAAlgorithm.CENTRAL_ATTRACTOR,
            brush_size=2,
            symmetry=DLASymmetry.HORIZONTAL)
