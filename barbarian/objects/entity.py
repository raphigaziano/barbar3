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

    def filter_by_components(self, *component_classes):
        """ Return all entitites containing all passed components types. """
        for e in iter(self):
            for c in component_classes:
                if not e.has_component(c):
                    break
            else:
                yield e

    def filter_by_property(self, property_name, property_value=None):
        """
        Return all entities possessing the given property.

        If property_value is passed, then entities will be further filtered
        by wheter their queried property is set to the passed value.

        """
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

    # An Alias to the NullProperty Class for easier checks
    NULL_PROPERTY = NullProperty()
    # Specialized entitiy classes can specify a number of required components
    # in this list.

    def __init__(self, entity_name=None, **kwargs):

        if entity_name is not None:
            self.entity_name = entity_name
        else:
            self.entity_name = self.__class__.__name__

        self._components = []
        for c_name, c_val in kwargs.items():
            CompCls = getattr(components, c_name)
            if CompCls is not None and not self.has_component(c_name):
                c_val['entity'] = self
                self.add_component(CompCls(**c_val))
            # else:
            #     setattr(self, c_name, c_val)

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

    def has_component(self, component):
        """
        Check if entity contains the queried component, or a subclass thereof.

        component should be a component class (not an instance), or its class
        name as a string.
        """
        for c in self._components:
            cls = c.__class__
            try:
                if issubclass(cls, component):
                    return True
            except TypeError:
                if cls.__name__ == component:
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

    def set_property(self, prop_name, prop_val):
        """ Try and set attr on a component. """
        # TODO:
        # Ensuring we only update the first component having this prop by
        # returning after we found and updated it.
        # Is this the right behaviour ? Parameterize this ?
        # Also, Should we raise an error if prop_name can't be found ?
        # /!\ DOC & TEST ME when this is is settled /!\
        for c in self._components:
            if hasattr(c, prop_name):
                setattr(c, prop_name, prop_val)
                return

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

    def update(self, **kwargs):
        """ Update all Updatable components. """
        for c in self._components:
            if hasattr(c, 'update'):
                c.update(**kwargs)

    def on_bump(self, DUMARG=None):
        # call all components on_bump
        return self.__getattr__('on_bump')  # TEMPO HACK
