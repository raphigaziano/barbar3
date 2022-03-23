"""
State management.

"""
from barbarian.events import Event


class GameState:
    """ Utility class to store and update state. """

    def __init__(self):

        self._state: dict = {}
        self.prev: GameState = None

    def __getattr__(self, attr_name):
        if attr_name in self._state:
            return self._state[attr_name]
        clsname = self.__class__.__name__
        raise AttributeError(
            f"{clsname} object has no attribute '{attr_name}'")

    def map_batch(self, game):
        # Attempt to optimise. No significant gain
        # over list comps :/
        level = game.current_level
        map_ = level.map
        arr_length = map_.w * map_.h

        batched = {
            'map': {
                'width': map_.w,
                'height': map_.h,
                'cells': [None] * arr_length,
                'bitmask_grid': [None] * arr_length if map_.bitmask_grid else None,
            },
            'map_snapshots': [[None] * arr_length] * len(level.map_snapshots),
            'visible_cells': [None] * arr_length,
            'explored_cells': [None] * arr_length,
        }

        for i, c in enumerate(map_.cells):
            x, y = map_._idx_to_cartesian(i)
            # if full_update:
            batched['map']['cells'][i] = c.value
            if map_.bitmask_grid:
                batched['map']['bitmask_grid'][i] = map_.bitmask_grid.cells[i]
            for j, snap in enumerate(level.map_snapshots):
                snap_cells = batched['map']['map_snapshots'][j]
                snap_cells[i] = snap.cells[i].value
            # /endif
            batched['visible_cells'][i] = (x, y) in game.player.fov.visible_cells
            batched['explored_cells'][i] = (x, y) in level.explored
            # if debug:
            #     pass
            #     # pathmap

        return batched

    def update(self, game):
        """
        Build the state dictionnary which will be sent to the client.

        Should be called everytime we need to notify some changes.

        """
        self.prev = self
        self._state = {
            'tick': game.ticks,
            'player': game.player.serialize(),
            'current_depth': game.world.current_depth,
            'max_depth': game.world.max_depth,
            'map': game.current_level.map.serialize(),
            'map_snapshots':
                [m.serialize() for m in game.current_level.map_snapshots],
            'visible_cells': [
                (x, y) in game.player.fov.visible_cells
                for x, y, _ in game.current_level.map],
            'explored_cells': [
                (x, y) in game.current_level.explored
                for x, y, _ in game.current_level.map],
            'actors': [e.serialize() for e in game.actors],
            'items': [e.serialize() for e in game.current_level.items.all],
            'props': [e.serialize() for e in game.current_level.props.all],
            # 'last_action': game.last_action,
            'last_events': [
                e.serialize() for e in
                Event.get_current_events(game.ticks, flush=True)],
        }

        # batched = self.map_batch(game)
        # self._state.update(batched)

        # DEBUGGING
        m = game.current_level.map

        from barbarian.utils.structures.dijkstra import DijkstraGrid
        path_map = DijkstraGrid.new(
            m.w, m.h,
            (game.player.pos.x, game.player.pos.y),
            (2, *game.current_level.exit_pos),
            predicate=lambda x, y, _: not m.cell_blocks(x, y),
            cost_function=lambda _, __, ___: 1
        )
        self._state['map']['pathmap'] = path_map.cells

        # Still DEBUGING
        self._state['spawn_zones'] = list(
            z for z in game.current_level.spawn_zones)

    def clear(self):
        self._state = {}
        self.prev = None

    @property
    def full(self):
        return self._state
