# -*- coding: utf8 -*-
"""
barbarian.dungeon.py
====================

Dugeon & Dungeon levels.

"""
from barbarian import libtcodpy as libtcod
from barbarian.mapgen import make_map


class Level(object):

    def __init__(self):
        self.map = make_map()
        self.fov_map = libtcod.map_new(self.map.w, self.map.h)
        for x, y, cell in self.map:
            libtcod.map_set_properties(
                self.fov_map, x, y, not cell.blocks_sight, not cell.blocks
            )
        self.objects = []

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
        libtcod.map_compute_fov(
            self.fov_map, from_x, from_y, 10, True, 0   # TODO: use constants
        )
        for x, y, cell in self.map:
            if libtcod.map_is_in_fov(self.fov_map, x, y):
                self.map.get_cell(x, y).explored = True


class Dungeon(object):

    """ Level Container. """

    def __init__(self):
        self.levels = []
        self.current_level = Level()

        self.levels.append(self.current_level)
