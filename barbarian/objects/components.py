# -*- coding: utf8 -*-
"""
barbarian.objects.components.py
===============================

"""
# TODO: Better naming and split comps into several files.
import logging

logger = logging.getLogger(__name__)


class MissingRequiredProperty(Exception):
    pass

class BaseComponent(object):

    def _get_required_arg(self, arg_name, args_dict):
        """
        Attempt to retrieve `arg_name` from a kwarg dict and raise a specific
        exception in case of failure.

        """
        try:
            return args_dict.pop(arg_name)
        except KeyError as e:
            # TODO: log & nicer err msg
            raise MissingRequiredProperty(e)

    def _get_default_arg(self, arg_name, args_dict, default=None):
        """
        Attempt to retrieve `arg_name` from a kwarg dict and return `default`
        if it could not be found.

        """
        return args_dict.pop(arg_name, default)


class PositionComponent(BaseComponent):

    def __init__(self, **kwargs):
        self.x = self._get_required_arg('x', kwargs)
        self.y = self._get_required_arg('y', kwargs)
        self.blocks = self._get_default_arg('blocks', kwargs, True)
        super(PositionComponent, self).__init__(**kwargs)

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

class VisibleComponent(BaseComponent):

    def __init__(self, **kwargs):
        self.char = self._get_required_arg('char', kwargs)
        super(VisibleComponent, self).__init__(**kwargs)

