# -*- coding: utf8 -*-
"""
barbarian.objects.entity.py
============================

"""
from barbarian.objects import components

class Entity(object):
    """ Base Entity Class. """
    pass

class Actor(
    Entity,
    components.MobileComponent,
    components.BumpComponent,
    components.VisibleComponent,
):
    """ Dummy Actor object """
    pass


