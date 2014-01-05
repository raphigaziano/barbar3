# -*- coding: utf8 -*-
"""
barbarian.objects.entity.py
============================

"""
import logging

from barbarian.objects import components

logger = logging.getLogger(__name__)

class NullProperty(object):
    pass

class EntityContainer(list):

    def filter_by_component(self, component_class):
        for e in iter(self):
            if e.has_component(component_class):
                yield e

    def filter_by_property(self, property_name, property_value=None):
        for e in iter(self):
            if e.has_property(property_name):
                if (property_value is not None and
                    getattr(e, property_name) != property_value
                ):
                    continue
                yield e

class Entity(object):

    """ Base Entity Class. """

    # TODO: Entities will probably need some common attrs like a name, id...

    NULL_PROPERTY = NullProperty()
    # Standard Components some specializing entities will automagically get.
    base_components = ()

    def __init__(self, **kwargs):

        # kwargs and super call: temporary fix (inheriting classes still need
        # it)
        super(Entity, self).__init__(**kwargs)
        self._components = []
        for c in self.base_components:
            self.add_component(c)

    def add_component(self, component, index=-1):
        self._components.insert(index, component)

    def push_component(self, component):
        self._component.insert(0, component)

    def pop_component(self):
        """
        Pop component off the front of the internal component list.

        See push_component.

        """
        return self._components.pop(0)

    def has_component(self, component):
        """
        Check if entity contains the queried component, or a subclass thereof.

        component should be a component class, not an instance.
        """
        for c in self._components:
            if issubclass(c.__class__, component):
                return True
        return False

    def has_property(self, property_name):
        """
        Check if one of the contained components has the queried property.

        """
        for c in self._components:
            if hasattr(c, property_name):
                return True
        return False

    def get(self, property_name, default=NULL_PROPERTY):
        """
        Dict like get method.

        Return the queried property, or default if it can't be found.

        """
        for c in self._components:
            if hasattr(c, property_name):
                return getattr(c, property_name)
        return default

    def __getattr__(self, attr_name):
        """ Log invalid attribute access, but don't raise exceptions. """
        # NOTE: This might be an *AWFUL* idea \o/
        # Perf idea: Cache a component-attribute mapping
        # (Updated on component list modifications).
        attr = self.get(attr_name)
        if attr is self.NULL_PROPERTY:
            logger.warning('%s has no %s attribute', self, attr_name)
            # raise an error ?
        return attr

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
        self.get('move')(dx, dy, level)
        level.compute_fov(self.x, self.y)
        # TODO: update cam here
