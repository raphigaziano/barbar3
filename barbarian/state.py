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

    def update(self, game):
        """
        Build the state dictionnary which will be sent to the client.

        Should be called everytime we need to notify some changes.

        """
        self.prev = self
        self._state = {
            'tick': game.ticks,
            'player': game.player.serialize(),
            'inventory': game.player.inventory.serialize(),
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
            'distance_map': game.current_level.distance_map.cells,
            'actors': [e.serialize() for e in game.actors],
            'items': [e.serialize() for e in game.current_level.items.all],
            'props': [e.serialize() for e in game.current_level.props.all],
            # 'last_action': game.last_action,
            'last_events': [
                e.serialize() for e in
                Event.get_current_events(game.ticks, flush=True)],
        }

        # DEBUGING
        self._state['spawn_zones'] = list(
            z for z in game.current_level.spawn_zones)

    def clear(self):
        self._state = {}
        self.prev = None

    @property
    def full(self):
        return self._state
