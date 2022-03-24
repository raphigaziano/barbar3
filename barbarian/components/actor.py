"""
Components defining an acting entity.

"""
from barbarian.components.base import Component


class Actor(Component):
    __serialize__ = True

    is_player: bool = False


class Health(Component):
    __serialize__ = True

    hp: int

    @property
    def is_dead(self):
        return self.hp <= 0


class Stats(Component):
    __serialize__ = True

    strength: int


class Fov(Component):
    __serialize__ = ['range']

    range: int

    def __post_init__(self):
        self.reset()

    def reset(self):
        self.visible_cells = set()
        self.explored = set()

    def compute(self, level, from_x, from_y, update_level=False):
        """
        Recompute fov from the (from_x, from_y) position.

        (Typically, (from_x, from_y) will be the player's current position).

        """
        self.visible_cells.clear()

        # TODO: use settings constants.
        level.fov_map.compute_fov(
            from_x, from_y, radius=self.range, light_walls=True, algorithm=0)

        for y in range(level.fov_map.height):
            for x in range(level.fov_map.width):
                if level.fov_map.fov[y,x]:
                    self.visible_cells.add((x,y))
                    self.explored.add((x, y))
                    if update_level:
                        level.explored.add((x,y))

    def is_in_fov(self, x, y):
        return (x, y) in self.visible_cells
