"""
Base component logic. Mainly metaclass shenanigans.

"""
import logging
from collections.abc import Iterable
from dataclasses import dataclass, asdict

from barbarian.utils.data import make_hash


logger = logging.getLogger(__name__)


class _ComponentMeta(type):
    """
    Metaclass for components.

    Automate registration of any component implementing this metaclass
    (via inheriting from `Component`), as well as inheriting from dataclass,
    flyweight behaviour and any other magic that may pop up.

    """

    __COMPONENT_MAP__ = {}

    def __new__(cls, name, bases, attrs, **kwargs):
        new_cls = dataclass(super().__new__(cls, name, bases, attrs, **kwargs))

        if (attr_name := new_cls.get_attr_name()) != 'component':
            _ComponentMeta.__COMPONENT_MAP__[attr_name] = new_cls
            logger.debug('Registered component: %s, %s', attr_name, new_cls)

        if new_cls.__flyweight__:
            # Set instances dict on flyweight components right now,
            # otherwise this won't be set until the first instanciation.
            # Not a big deal but could be confusing when testing / debuging.
            # Also, see Component.mangle docs for why we're bothering.
            mangled_attr_name = new_cls.mangle('__flyweight_instances')
            setattr(new_cls, mangled_attr_name, {})

        return new_cls

    def __call__(cls, *args, **kwargs):

        if cls.__flyweight__:

            cls_instances = getattr(cls, cls.mangle('__flyweight_instances'))

            hash_kwargs = kwargs.copy()
            instance_hash = make_hash(hash_kwargs)

            if instance_hash not in cls_instances:
                new_instance = super().__call__(*args, **kwargs)
                setattr(new_instance, '_initialized', True)
                cls_instances[instance_hash] = new_instance

            return cls_instances[instance_hash]

        return super().__call__(*args, **kwargs)


class Component(metaclass=_ComponentMeta):
    """
    Base class for components.

    Implements auto-registration and dataclass interface (via `_ComponentMeta`)
    as well as basic serialization logic.

    Components can define the following meta attributes:

        - __attr_name__: Name used to reference the component. This
            will be repercuted en Entities owning this component, ie:

            $ class DummyComponent(Component):
                  __attr_name__ = "custom_name"

            $ e = Entity()
            $ e.add_component(DummyComponent())
            $ e.custom_name == <component_instance>

            If not defined, then the registered name will be ClassName.lower(),
            ie "dummycomponent" in the above exemple.

        - __serialize__: Determine how this component should be serialized.

            Can be:
            - False (default): whole component will be ignored.
            - True: all fields will be included
            - list of field names (as strings) that will be included.

        - __flyweight__: Only one instance will be created, to be shared
          amoong all entities using this component. Ideal for Flag or Type
          type components, but beware: changes to the component's state will
          be repercuted to *all* instances using it.

    Component definition follows the dataclass interface:

    $ class MyComponent(Componenet):
    $     x: int
    $     y: str = 'wut'
    $     etc...

    """

    __attr_name__ = None
    __serialize__ = False
    __flyweight__ = False

    _initialized = False    # Will be set by _ComponentMeta.__call__

    @classmethod
    def mangle(cls, attr_name):
        """ Manually mangle dunder name to avoid scoping shenanigans. """
        # This may be overkill (just using a single undescore pseudo
        # private attribute is technically enough), but at least for flyweight
        # components, having potential child classes share their instances
        # with their parents smells like nasty bugs galore...
        if not attr_name.startswith('__'):
            raise ValueError('No need to mangle a name not starting with __')
        return f'_{cls.__name__}{attr_name}'

    @classmethod
    def get_attr_name(cls):
        return cls.__attr_name__ or cls.__name__.lower()

    @property
    def attr_name(self):
        return self.__class__.get_attr_name()

    def __setattr__(self, attr_name, v):
        if self.__flyweight__ and self._initialized:
            raise AttributeError(
                f'Modifying attribute <{attr_name}> on flyweight instance of '
                f'component <{self.__class__} ({id(self)})> is not allowed.'
            )
        super().__setattr__(attr_name, v)

    def as_dict(self):
        return asdict(self)

    def serialize(self):
        """
        Default seriailization logic. See class docstring for more info.

        """
        if self.__serialize__:
            data = self.as_dict()
            if isinstance(self.__serialize__, Iterable):
                for k in list(data):
                    if k not in self.__serialize__:
                        data.pop(k)
            return data
        return None


class Named(Component):
    """ Allow entity to be named. """
    name: str


class Typed(Component):
    """ Simple typing for entities. """
    __flyweight__ = True
    __serialize__ = True

    type: str


class Visible(Component):
    """
    Visibility status (ie can the entity be seen by other actors).

    Include a glyph property for internal representation.

    """
    # FIXME: rename this as RenderInfo or something (make it flyweight)
    # and use Visible for actual game info (invis, etc).
    # We don't need the game info for now tho.
    __serialize__ = True

    glyph: str = ""
