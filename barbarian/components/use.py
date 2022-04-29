"""
Components to define an item, prop... effects on activation (ie: 
case a spell from a scroll or want, inflict damage for a trap, etc...)

"""
from enum import auto
from dataclasses import field, KW_ONLY

from barbarian.utils.types import StringAutoEnum, FrozenDict
from barbarian.components.base import Component
from barbarian.actions import Action


class PropActivationMode(StringAutoEnum):

    ACTOR_ON_TILE = auto()
    ACTOR_BUMP = auto()


class Usable(Component):
    __flyweight__ = True

    action_data: dict
    _action_data: FrozenDict = field(default=None, init=False, repr=False)
    use_key: str = ""

    @property
    def action_data(self):
        return self._action_data.copy() if self._action_data is not None else None

    @action_data.setter
    def action_data(self, v):
        self._action_data = FrozenDict(v)

    def get_action(self, actor, entity):
        """
        Return an `Action` instance built from `action_data` and the
        passed `actor`, `entity` pair.

        """
        new_action_args = self.action_data
        action = Action.from_dict(new_action_args)
        action.set_actor_and_target(actor, entity)
        return action

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
        del kwargs['_action_data']
        kwargs['action_data'] = new_action_data
        return cls(**kwargs)


class Trigger(Usable):

    _: KW_ONLY
    activation_mode: PropActivationMode

    def __post_init__(self):
        self.activation_mode = PropActivationMode(self.activation_mode)


class Consumable(Component):
    __serialize__ = True

    charges: int = 1
    max_charges: int = field(default=None, init=False)

    def __post_init__(self):
        self.max_charges = self.charges

    @property
    def depleted(self):
        return self.charges == 0


class Openable(Component):
    __serialize__ = True

    open: bool = False


class Edible(Component):
    __serialize__ = True

    nutrition: int
