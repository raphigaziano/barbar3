"""
Level and world storage.

"""
import logging

import tcod

from barbarian.utils.rng import Rng
from barbarian.utils.structures.grid import (
    EntityGrid, GridContainer, OutOfBoundGridError)
from barbarian.genmap import builders
from barbarian.spawn import spawn_level


logger = logging.getLogger(__name__)


class Level:
    """
    A playable level, containing a map as well as a list of all
    entities inhabiting it.

    Entities are divided into three lists/indices: actors, props and items.

    It's up to the spawning code to assign them to the right container.

    """

    def __init__(self, w, h, depth=1):

        self.w, self.h = w, h
        self.depth = depth
        self.map = None
        self.fov_map = None
        self.explored = set()

        self.start_pos = None, None
        self.exit_pos = None, None
        self.spawn_zones = []
        self.map_snapshots = []

        self.actors = EntityGrid(self.w, self.h)
        self.props = EntityGrid(self.w, self.h)
        self.items = GridContainer(self.w, self.h)

    def build_map(self, map_debug=False):
        """
        Chose a random map builder and build a new level map.

        Start / exit positions, map snapshots and spawn zones generated
        will be stored on the level.

        Note: we're only concerned with building the map here, and
        do not bother initializing the fov map or populating the
        level.

        """
        builder = Rng.dungeon.choice([
            builders.SimpleMapBuilder(debug=map_debug),
            builders.BSPMapBuilder(debug=map_debug),
            builders.BSPInteriorMapBuilder(debug=map_debug),
            builders.CellularAutomataMapBuilder(debug=map_debug)
        ])
        # builder = builders.CellularAutomataMapBuilder(debug=map_debug)
        logger.debug('Selected map builer: %s', type(builder))

        self.map = builder.build_map(self.w, self.h, self.depth)

        self.start_pos = builder.get_starting_position()
        self.exit_pos = builder.get_exit_position()
        self.spawn_zones = builder.get_spawn_zones()

        self.map_snapshots = builder.snapshots
        self.map.compute_bitmask_grid()

    def init_fov_map(self):
        """
        Initialize the fov map.

        Make sure to call it *after* the passed level's map has been
        built and the level has been populated.

        """
        if self.fov_map is None:
            self.fov_map = tcod.map.Map(self.map.w, self.map.h)
        for x, y, _ in self.map:
            self.fov_map.transparent[y,x] = (
                not self.map.cell_blocks(x, y) and
                not (self.actors[x,y] is not None
                 and self.actors[x,y].physics.blocks_sight) and
                not (self.props[x,y] is not None
                 and self.props[x,y].physics.blocks_sight)
            )
            # self.fov_map.walkable[y,x] = (
            #     not self.map.cell_blocks(x, y) and
            #     not any(e.physics.blocks for e in self.props[x,y])
            # )

    def get_map_cell(self, x, y):
        """ Shortcut to access map cells direcly. """
        return self.map.get_cell(x, y)

    def is_blocked(self, x, y):
        """
        Return True if the (x, y) cell is blocked or occupied, False
        otherwise.

        """
        def _cell_occupied(entity):
            return entity is not None and entity.physics.blocks

        try:
            if _cell_occupied(self.props[x,y]):     return True
            if _cell_occupied(self.actors[x,y]):    return True
            return self.map.cell_blocks(x, y)
        except OutOfBoundGridError:
            return True

    def move_actor(self, actor, dx, dy):
        """
        Moved `actor` along the `dx`, `dy` vector, and update
        the internal actor list.

        Note: All entity movement should use this function, otherwise
        the position index won't be updated and cause shenanigans.

        Not sure how to enforce this tho...

        """
        newx, newy = actor.pos.x + dx, actor.pos.y + dy
        if not self.is_blocked(newx, newy):
            self.actors.remove_e(actor)
            actor.pos.x, actor.pos.y = newx, newy
            self.actors.add_e(actor)
            return True
        return False

    def populate(self):
        """ Call spawning function on this level. """
        spawn_level(self, self.spawn_zones)

    def enter(self, actor):
        """
        Add `actor` (typically the player) to the level and recompute
        its fov.

        """
        self.actors.add_e(actor)
        if actor.fov:
            actor.fov.reset()
            actor.fov.compute(
                self, actor.pos.x, actor.pos.y, update_level=actor.is_player)


class World:
    """
    Level container, responsible for keeping track of which level
    we're currently playing and generating new levels as needed.

    """

    def __init__(self, level_w, level_h):
        self.level_w, self.level_h = level_w, level_h

        self._current_depth = 1
        self.max_depth = 1
        self.levels = []

    @property
    def current_depth(self):
        return self._current_depth

    @current_depth.setter
    def current_depth(self, v):
        self._current_depth = v
        if self._current_depth > self.max_depth:
            self.max_depth = self._current_depth

    @property
    def _cur_level_idx(self):
        return self.current_depth - 1

    @property
    def current_level(self):
        return self.levels[self._cur_level_idx]

    def insert_level(self, level, replace_current=False):
        """
        Actually add level to the level list.

        if `replace_current` is True, then the current level will be
        regenerated and current_depth will not be changed (this is
        mostly useful for debugging).

        """
        if replace_current:
            self.levels[self._cur_level_idx] = level
        else:
            self.levels.append(level)

    def new_level(self, depth=None, debug=False):
        """ Generate and return a new level. """
        level = Level(
            self.level_w, self.level_h, depth=depth or self.current_depth)
        level.build_map(map_debug=debug)
        level.populate()
        level.init_fov_map()

        return level

    def change_level(self, depth_delta, player, debug=False):
        """
        Change the current level.

        Overall behavour will depend on `depth_delta`:
        - if it is positive, a new level will be generated.
        - if it is negative, then we'll backtrack to the previous
          level.
        - if it is 0, then the current level will be regenerated.

        (Note, actual values are ignored, ie `change_level(1)` will
        act the same as `change_level(2)` or `change_level(47)`.)

        No matter the changing behaviour, the passed actor will be
        removed from the previous level and added to the new one.

        """
        assert self.levels

        self.current_level.actors.remove_e(player)

        if depth_delta >= 0:
            if depth_delta >= 1:
                self.current_depth += 1
            new_level = self.new_level(self.current_depth, debug=debug)
            self.insert_level(new_level, replace_current=depth_delta == 0)
            player.pos.x, player.pos.y = self.current_level.start_pos
        else:
            self.current_depth -= 1
            player.pos.x, player.pos.y = self.current_level.exit_pos

        self.current_level.enter(player)
