# -*- coding: utf8 -*-
"""
barbarian.objects.mapobjects.py
===============================

"""
from barbarian.objects.entity import Entity
from barbarian.objects.components import SolidComponent#, PositionComponent


class MapTile(Entity, SolidComponent):#, PositionComponenet):

    """
    A Basic Map Tile.

    Define whether this part of the map blocks movement or sight,
    & tracks map infos (explored status, noise or scent levels...).

    """
    def __init__(self, **kwargs):
        super(MapTile, self).__init__(**kwargs)
        self.explored = False
