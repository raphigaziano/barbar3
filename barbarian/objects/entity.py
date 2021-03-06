# -*- coding: utf8 -*-
"""
barbarian.objects.entity.py
============================

"""
import logging

from barbarian.objects import components

logger = logging.getLogger(__name__)

class NullProperty(object):

    """ Oh my... """

    def __getattr__(self, attr_name):
        return NullProperty()

    def __call__(self, *args, **kwargs):
        pass

class Entity(object):

    """ Base Entity Class. """

    # TODO: Entities will probably need some common attrs like a name, id...

    def __getattr__(self, attr_name):
        """ Log invalid attribute access, but don't raise exceptions. """
        # NOTE: This might be an *AWFUL* idea \o/
        logger.warning('%s has no %s attribute' % (self, attr_name))
        return NullProperty()


class Actor(
    Entity,
    components.MobileComponent,
    components.SolidComponent,
    components.BumpComponent,
    components.VisibleComponent,
):
    """ Dummy Actor object """
    pass

class Player(Actor):

    """ Player Object - Basically an actor with some custom behaviour. """

    def move(self, dx, dy, level):
        super(Player, self).move(dx, dy, level)
        level.compute_fov(self.x, self.y)
        # TODO: update cam here
