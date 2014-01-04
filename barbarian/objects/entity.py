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
        return NullProperty()

    def __cmp__(self, other):
        # Cannot override is operator (whish is prolly for the best...),
        # so dummy_prop is NullProperty won't work. Use == instead.
        return 0 if other.__class__ is self.__class__ else 1

    def __hash__(self):
        return id(self.__class__)

class Entity(object):

    """ Base Entity Class. """

    # TODO: Entities will probably need some common attrs like a name, id...

    # An Alias to the NullProperty Class for easier checks
    NULL_COMPONENT = NullProperty
    # Standard Components some specializing entities will automagically get.
    base_components = ()

    def __init__(self, **kwargs):

        self._components = []
        for C in self.base_components:
            self.add_component(C(**kwargs))

    def add_component(self, component, index=None):
        """
        Add component to the internal componenet list.

        If index is None, componenet will be simply appended at the end of the
        list. Else, it will be inserted at the specified index, with a regular
        list.insert call.

        """
        if index is None:
            self._components.append(component)
        else:
            self._components.insert(index, component)

    # def remove_componenet(component): self._components.remove(component) ?

    def push_component(self, component):
        """
        Push component on top of the internal componenet list.

        NOTE: Componenet will be pushed to the *front* of the list (ie at index
        0). This means pushed component will override other ones with the same
        attr or method names when trying to access those.

        This behaviour is still experimental and might be canned.

        """
        self._components.insert(0, component)

    def pop_component(self):
        """
        Pop component off the front of the internal component list.

        See push_component.

        """
        return self._components.pop(0)

    def __getattr__(self, attr_name):
        """ Log invalid attribute access, but don't raise exceptions. """
        # NOTE: This might be an *AWFUL* idea \o/
        # Perf idea: Cache a component-attribute mapping
        # (Updated on component list modifications).
        for c in self._components:
           if hasattr(c, attr_name):
               return getattr(c, attr_name)
        logger.warning('%s has no %s attribute', self, attr_name)
        return NullProperty()

class Actor(Entity):

    """ Dummy Actor object """

    base_components = (
        components.MobileComponent,
        components.SolidComponent,
        components.BumpComponent,
        components.VisibleComponent,
    )

class Player(Actor):

    """ Player Object - Basically an actor with some custom behaviour. """

    def move(self, dx, dy, level):
        # super(Player, self).move(dx, dy, level)
        self._components[0].move(dx, dy, level)    # OUCH!
        level.compute_fov(self.x, self.y)
        # TODO: update cam here
