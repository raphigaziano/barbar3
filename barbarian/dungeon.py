# -*- coding: utf8 -*-
"""
barbarian.dungeon.py
====================

Dugeon & Dungeon levels.

"""
from barbarian.mapgen import make_map


class Level(object):

    def __init__(self):
        self.map = make_map()
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
        # Dummy object collision: any object blocks
        for obj in self.get_objects_at(x, y):
            if obj.blocks:
                return True
        return self.map.get_cell(x, y).blocks

class Dungeon(object):

    """ Level Container. """

    def __init__(self):
        self.levels = []
        self.current_level = Level()

        self.levels.append(self.current_level)
