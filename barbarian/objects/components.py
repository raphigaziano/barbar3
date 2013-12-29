# -*- coding: utf8 -*-
"""
barbarian.objects.components.py
===============================

"""
# TODO: Better naming and split comps into several files.
import logging

logger = logging.getLogger(__name__)


class PositionComponent(object):

    def __init__(self, x, y, *args, **kwargs):
        self.x, self.y = x, y
        self.blocks = kwargs.pop('blocks', True)
        super(PositionComponent, self).__init__(*args, **kwargs)

class MobileComponent(PositionComponent):

    def move(self, dx, dy, level):
        # Try and move to x+dx, y+dy
        new_x, new_y = self.x + dx, self.y + dy
        if level.is_blocked(new_x, new_y):
            logger.debug('Cannot move to cell %d-%d' % (new_x, new_y))
        else:
            self.x, self.y = new_x, new_y

        # Call any bumped objects bump handler
        for obj in level.get_objects_at(new_x, new_y):
            obj.on_bump(self)

        # return new position ?

class BumpComponent(PositionComponent):

    def on_bump(self, bumper):
        logger.debug('BUMP!')

class VisibleComponent(object):

    def __init__(self, char, *args, **kwargs):
        self.char = char
        super(VisibleComponent, self).__init__(*args, **kwargs)

