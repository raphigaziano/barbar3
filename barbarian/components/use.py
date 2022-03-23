"""
Components to define an item, prop... effects on activation (ie: 
case a spell from a scroll or want, inflict damage for a trap, etc...)

"""
from enum import auto
from dataclasses import field, KW_ONLY

from barbarian.utils.types import StringAutoEnum, FrozenDict
from barbarian.components.base import Component


class UseTarget(StringAutoEnum):

    SELF = auto()
    ACTOR = auto()


class PropActivationMode(StringAutoEnum):

    ACTOR_ON_TILE = auto()
    ACTOR_BUMP = auto()


class Usable(Component):
    __flyweight__ = True

    action: dict
    _action: FrozenDict = field(default=None, init=False, repr=False)
    target: UseTarget = UseTarget.SELF
    use_key: str = ""

    def __post_init__(self):
        self.target = UseTarget(self.target)

    @property
    def action(self):
        return self._action.copy() if self._action is not None else None

    @action.setter
    def action(self, v):
        self._action = FrozenDict(v)

    def get_actor_and_target(self, user, usable_entity):
        """
        Return the right actor and target depending on `self.target` mode.

        Return data as a dict it order to easily update an `Action`
        argument dict.

        """
        match self.target:
            case UseTarget.ACTOR:
                return {'actor': usable_entity, 'target': user}
            case UseTarget.SELF:
                return {'actor': user, 'target': usable_entity}

    def new_action(self, new_action_data):
        """
        Return a new component with the passed action_data.

        Use this method to modify an entity's use or trigger action
        instead of trying to mess directly with its action dict, which
        is verbotten because flyweight objects are shared between many
        entities.

        """
        cls = self.__class__

        kwargs = self.as_dict()# .copy()
        del kwargs['_action']
        kwargs['action'] = new_action_data
        return cls(**kwargs)


class Trigger(Usable):

    _: KW_ONLY
    activation_mode: PropActivationMode

    def __post_init__(self):
        super().__post_init__()
        self.activation_mode = PropActivationMode(self.activation_mode)


class Openable(Component):
    __serialize__ = True

    open: bool = False
