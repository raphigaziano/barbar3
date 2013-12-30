# -*- coding: utf8 -*-
"""
barbarian.objects.mapobjects.py
===============================

"""
from barbarian.objects.entity import Entity
from barbarian.objects.components import SolidComponent#, PositionComponent


class MapTile(Entity, SolidComponent):#, PositionComponenet):

    def __init__(self, **kwargs):
        super(MapTile, self).__init__(**kwargs)
        self.explored = False
