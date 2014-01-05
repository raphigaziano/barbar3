# -*- coding: utf8 -*-
"""
barbarian.dungeon.py
====================

Dugeon & Dungeon levels.

"""
from barbarian import libtcodpy as libtcod
from barbarian.mapgen import make_map
from barbarian.objects.entity import EntityContainer


class Level(object):

    """
    Game Level (in a dungeon or not - Level here basiclly means a play area.

    Contains the level map(s) and a list of all items and actors inhabiting it.

    """

    def __init__(self):
        self.map = make_map()
        self.fov_map = libtcod.map_new(self.map.w, self.map.h)
        for x, y, cell in self.map:
            libtcod.map_set_properties(
                self.fov_map, x, y, not cell.blocks_sight, not cell.blocks
            )
        self.objects = EntityContainer()
        self.populate()

    def get_map_cell(self, x, y):
        """ Shortcut to access map cells directly. """
        return self.map.get_cell(x, y)

    def get_objects_at(self, x, y):
        """ Yield all objects located at (x,y). """
        for o in self.objects:
            if o.x == x and o.y == y:
                yield o

    def is_blocked(self, x, y):
        """ Return True of the (x, y) cell is blocked, False otherwise. """
        for obj in self.get_objects_at(x, y):
            if obj.blocks:
                return True
        return self.map.get_cell(x, y).blocks

    def compute_fov(self, from_x, from_y):
        """
        Recompute fov based on the (from_x, from_y) position.

        (Typically, (from_y, from_y) will be the player's current position).

        """
        libtcod.map_compute_fov(
            self.fov_map, from_x, from_y, 10, True, 0   # TODO: use constants
        )
        for x, y, cell in self.map:
            if libtcod.map_is_in_fov(self.fov_map, x, y):
                cell.explored = True

    def is_in_fov(self, x, y):
        """
        Return whether map pos (x, y) is in fov.

        Shortcut for calling libtcod.map_is_in_fov(map, x, y)

        """
        return libtcod.map_is_in_fov(self.fov_map, x, y)

    def is_obj_in_fov(self, obj):
        """
        Return whether map obj is in fov.

        Shortcut for calling libtcod.map_is_in_fov(map, obj.x, obj.y)

        """
        return self.is_in_fov(obj.x, obj.y)

    def populate(self):
        """ Stub method """
        from barbarian.utils import rng
        from barbarian.objects.entity import Actor
        for _ in range(10):
            x = rng.randrange(0, self.map.w)
            y = rng.randrange(0, self.map.h)
            while self.map.get_cell(x, y).blocks:
                x = rng.randrange(0, self.map.w)
                y = rng.randrange(0, self.map.h)
            self.objects.append(Actor(x=x, y=y, char='r'))

    def update(self):
        """ STUB """
        pass

class Dungeon(object):

    """ Level Container. """

    # IDEA: remove, and replace with a sub_level attr in Level ?

    def __init__(self):
        self.levels = []
        self.current_level = Level()

        self.levels.append(self.current_level)
