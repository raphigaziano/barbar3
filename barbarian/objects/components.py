# -*- coding: utf8 -*-
"""
barbarian.objects.components.py
===============================

"""
# TODO: Better naming and split comps into several files.
import math
import logging

logger = logging.getLogger(__name__)


class MissingRequiredProperty(Exception):
    pass

class BaseComponent(object):

    """ Base, common component helpers. """

    @classmethod
    def _get_required_arg(cls, arg_name, args_dict):
        """
        Attempt to retrieve `arg_name` from a kwarg dict and raise a specific
        exception in case of failure.

        """
        try:
            return args_dict.pop(arg_name)
        except KeyError as e:
            msg = '%s: Missing required property %s' % (cls.__name__, arg_name)
            logger.error(msg)
            raise MissingRequiredProperty(msg)

    @classmethod
    def _get_default_arg(cls, arg_name, args_dict, default=None):
        """
        Attempt to retrieve `arg_name` from a kwarg dict and return `default`
        if it could not be found.

        """
        return args_dict.pop(arg_name, default)


class PositionComponent(BaseComponent):

    """ Positionnal Attributes & Helpers. """

    def __init__(self, **kwargs):
        self.x = self._get_required_arg('x', kwargs)
        self.y = self._get_required_arg('y', kwargs)
        # TODO: move this attr in a separate SolidComponent
        self.blocks = self._get_default_arg('blocks', kwargs, True)
        super(PositionComponent, self).__init__(**kwargs)

    def distance_from(self, x, y):
        """
        Return the distance between the entity and a point located at (x, y).

        """
        return math.sqrt((x - self.x) ** 2 +(y - self.y) ** 2)

    def distance_from_obj(self, obj):
        """
        Return the distance between the entity and another positioned entity.

        """
        return self.distance_from(obj.x, obj.y)

class MobileComponent(PositionComponent):

    """ Movement Handler """

    def move(self, dx, dy, level):
        """
        Move the entity by a (dx, dy) vector.

        Also call the appropriate callback for any other entity we bump into.

        """
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

    """
    Bump Behaviour.

    Entities implementing this components will react according to their
    `on_bump` method whenever another objects steps on the cell they occupy.

    """

    def on_bump(self, bumper):
        logger.debug('BUMP!')

class VisibleComponent(BaseComponent):

    """ Minimal entity visual representation. """

    def __init__(self, **kwargs):
        self.char = self._get_required_arg('char', kwargs)
        super(VisibleComponent, self).__init__(**kwargs)
