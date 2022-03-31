"""
Components defining an acting entity.

"""
from dataclasses import field
from enum import auto

from barbarian.utils.types import StringAutoEnum
from barbarian.components.base import Component
from barbarian.settings import (
    DEFAULT_REGEN_RATE, DEFAULT_REGEN_AMOUNT,
    DEFAULT_HUNGER_RATE, MAX_HUNGER_SATIATION, HUNGER_STATES
)


class Actor(Component):
    __serialize__ = True

    is_player: bool = False


class Health(Component):
    __serialize__ = True

    hp: int
    max_hp: int = field(default=None, init=False)

    def __post_init__(self):
        self.max_hp = self.hp

    @property
    def is_dead(self):
        return self.hp <= 0


class Regen(Component):

    rate: int = DEFAULT_REGEN_RATE
    amount: int = DEFAULT_REGEN_AMOUNT


class HungerClock(Component):

    __attr_name__ = 'hunger_clock'
    __serialize__ = True

    rate: int = DEFAULT_HUNGER_RATE
    satiation: int = MAX_HUNGER_SATIATION

    @property
    def state(self):
        for state_name, threshold in HUNGER_STATES:
            if self.satiation < threshold:
                return state_name
        return 'full'

    @property
    def full(self):
        return self.state == 'full'

    @property
    def satiated(self):
        return self.state == 'satiated'

    @property
    def hungry(self):
        return self.state == 'hungry'

    @property
    def very_hungry(self):
        return self.state == 'very hungry'

    @property
    def starving(self):
        return self.state == 'starving'

    def serialize(self):
        return self.state


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
