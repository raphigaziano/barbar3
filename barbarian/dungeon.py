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

    def is_blocked(self, x, y):
        return self.map.get_cell(x, y).blocks

class Dungeon(object):

    def __init__(self):
        self.levels = []
        self.current_level = Level()

        self.levels.append(self.current_level)
