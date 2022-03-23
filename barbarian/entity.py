"""
Entity (ie component holder).

"""
import logging

from barbarian.components.base import Component


logger = logging.getLogger(__name__)


class Entity:
    """
    Represent any entity (actor, item, prop...) handled by the game.

    Entities are defined by their list of components.

    """

    _id_counter = 0

    def __init__(self):

        Entity._id_counter += 1
        self._id = Entity._id_counter

    @property
    def is_player(self):
        """ Shortcut to check if this entity is the player. """
        return self.actor and self.actor.is_player

    @property
    def name(self):
        if self.named: return self.named.name
        if self.typed: return self.typed.type
        return None

    def __repr__(self):
        comp_str = ', '.join(
            f'{cname}: {c}' for cname, c in self.components)
        return f'Entity<{self._id}>({comp_str})'

    def __getattr__(self, attr_name):
        if attr_name in Component.__COMPONENT_MAP__:
            return None
        raise AttributeError(attr_name)

    @property
    def components(self):
        for cname in Component.__COMPONENT_MAP__.keys():
            c = getattr(self, cname, None)
            if c:
                yield cname, c

    def add_component(self, cname, c=None):
        """
        Add a component to this enity.

        `c`omponent can be:
            - an already instanciated Component
            - a dictionary that will be passed to the relevent component
              contructor
            - None, in which case a component will be instanciated
              without any arguments.

        If `c` is not a component instance, then the component class
        which `__attr_name__` matches `cname` will be used to build
        the component.

        Note: if `cname` doesn't match an already built component's
        `__attr_name__`, then the later will be used as an attribute
        name and the former will be ignored.

        """
        if isinstance(c, Component):
            component = c
        else:
            try:
                cclass = Component.__COMPONENT_MAP__[cname]
            except KeyError:
                logger.warning('Component %s is not registered', cname)
                raise
            args = c if c else {}
            try:
                component = cclass(**args)
            except TypeError:
                logger.warning('Invalid args for component %s: %s', cclass, args)
                raise

        logger.debug(
            '<Entity %s>: Adding component %s: %s',
            self._id, cname, component)

        # Force attr name
        cname = component.attr_name
        setattr(self, cname, component)

    def remove_component(self, cname):
        """
        Remove (and deltes the corresponding attribute) component `cname`

        """
        if hasattr(self, cname):
            del self.__dict__[cname]

    def replace_component(self, new_component):
        attr_name = new_component.attr_name
        self.remove_component(attr_name)
        setattr(self, attr_name, new_component)

    def serialize(self):
        data = {
            'id': self._id,
            # 'name': self.named.name if self.named else '',
            'name': self.name or '',
            'type': self.typed.type if self.typed else '',
        }
        for cname, c in self.components:
            cdata = c.serialize()
            if not cdata:
                logger.debug(
                    'Ignored component %s while serializing entity %s', c, self)
                continue
            data[cname] = cdata

        return data

    @classmethod
    def from_dict(cls, data):
        """

        Build an entity directly from a dict representing the required
        components.

        """
        e = cls()
        for cname, cdata in data.items():
            e.add_component(cname, cdata)
        return e
