# -*- coding: utf8 -*-
"""
barbarian.dungeon.py
====================

Dugeon & Dungeon levels.

"""
from barbarian import libtcodpy as libtcod
from barbarian.mapgen import make_map
from barbarian.objects import components
from barbarian.objects.entity import EntityContainer


class Level(object):

    """
    Game Level (in a dungeon or not - Level here basiclly means a play area.

    Contains the level map(s) and a list of all items and actors inhabiting it.

    """

    def __init__(self):
        self.map = make_map()
        self.actors = EntityContainer()
        self.items = EntityContainer()
        self.populate()

    @property
    def objects(self):
        # TODO: Test me!
        return EntityContainer(self.actors + self.items)

    def get_map_cell(self, x, y):
        """ Shortcut to access map cells directly. """
        return self.map.get_cell(x, y)

    def get_objects_at(self, x, y):
        """
        Return all objects located at (x,y).

        Objects are container in a  EntityContainer list for further filtering
        by prop or component.
        """
        res = EntityContainer()
        for o in self.objects.filter_by_components(
            components.PositionComponent
        ):
            if o.x == x and o.y == y:
                res.append(o)
        return res

    def is_blocked(self, x, y):
        """ Return True of the (x, y) cell is blocked, False otherwise. """
        for obj in self.get_objects_at(x, y):
            if obj.blocks:
                return True
        return self.map.get_cell(x, y).blocks

    def populate(self):
        """ Stub method """
        from barbarian.utils import rng
        from barbarian.objects.factories import build_entity
        for _ in range(10):
            x = rng.randrange(0, self.map.w)
            y = rng.randrange(0, self.map.h)
            while self.map.get_cell(x, y).blocks:
                x = rng.randrange(0, self.map.w)
                y = rng.randrange(0, self.map.h)
            self.actors.append(build_entity('rat', x, y))
        for _ in range(5):
            x = rng.randrange(0, self.map.w)
            y = rng.randrange(0, self.map.h)
            while self.map.get_cell(x, y).blocks:
                x = rng.randrange(0, self.map.w)
                y = rng.randrange(0, self.map.h)
            self.actors.append(build_entity('parchment', x, y))

    def update(self, **kwargs):
        """ Update all actors on this level. """
        for a in self.actors.filter_by_property('update'):
            a.update(self, **kwargs)

class Dungeon(object):

    """ Level Container. """

    # IDEA: remove, and replace with a sub_level attr in Level ?

    def __init__(self):
        self.levels = []
        self.current_level = Level()

        self.levels.append(self.current_level)
