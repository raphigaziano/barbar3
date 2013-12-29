# -*- coding: utf8 -*-
"""
barbarian.entity.py
===================

"""
import logging

from barbarian import gui

logger = logging.getLogger(__name__)


class Entity(object):

    """ Base Entity Class. """

    def __init__(self, x, y, char=' '):
        self.x = x
        self.y = y
        self.char = char


class Player(Entity):

    """ Dummy Player object """

    def move(self, dx, dy, level):
        new_x, new_y = self.x + dx, self.y + dy
        if level.is_blocked(new_x, new_y):
            logger.debug('Cannot move to cell %d-%d' % (new_x, new_y))
            return
        self.x, self.y = new_x, new_y

