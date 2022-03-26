"""
Action handlers

"""
import logging
from enum import auto
from dataclasses import dataclass, field

from barbarian.utils.types import StringAutoEnum
from barbarian.entity import Entity
from barbarian.events import Event, EventType


logger = logging.getLogger(__name__)


class ActionError(Exception):
    """ Base exception for Action related errors. """


class UnknownActionTypeError(ValueError, ActionError):
    """ ActionType not defined. """


class ActionDataError(TypeError, ActionError):
    """ Invalid data dictionary."""


class ActionType(StringAutoEnum):

    REQUEST_INPUT = auto()
    IDLE = auto()
    MOVE = auto()
    XPLORE = auto()
    ATTACK = auto()
    INFLICT_DMG = auto()
    GET_ITEM = auto()
    DROP_ITEM = auto()
    USE_PROP = auto()
    OPEN_DOOR = auto()
    CLOSE_DOOR = auto()
    CHANGE_LEVEL = auto()


@dataclass()
class Action:
    """
    Represent a game action that can be taken by any game actor.

    Actions are aephemeral events, created either by ai or player input,
    and represent what an actor wants to do for this turn. They are then
    directly processed (dispatching logic to the relevant code) and discarded
    (we'll use events to keep track of what happens)

    Processing can either:
        - Return another action to be processed immediattly (ie, move action
          triggers an attack)
        - Reject the action, indicating the game loop that the requested
          action cannot be performed and that it should poll for a new one,
          without skipping the turn.
        - Accept the action and process it however it wants, which implies
          giving setting its valid flag to True at some point.

    The provided .accept() and .reject methods take care of setting the
    processed and valid flags as appropriate and raise an Event to be logged,
    storing the action result (as passed in by theprocessing code).

    Possible improvement: having to validate axplicitely each action is
    a little cumbersome. Maybe we can tweak the gameloop / overall interface
    to only look for a potentiel "invalid" state, and act like everything's fine
    by default ?

    """

    type: ActionType
    actor: Entity = None
    target: Entity = None
    data: dict = None

    processed: bool = field(init=False, repr=False, default=False)
    valid: bool = field(init=False, repr=False, default=None)
    msg: str = field(init=False, repr=False, default=None)

    def unpack(self):
        """ Shortcut to quickly retrieve action data. """
        return self.actor, self.target, self.data

    def accept(self, **kwargs):
        """ Mark the action as valid and emits an `ACTION_ACCEPTED` event. """
        self.processed = True
        self.valid = True
        self._emit_event(EventType.ACTION_ACCEPTED, **kwargs)

    def reject(self, **kwargs):
        """ Mark the action as invalid and emits an `ACTION_REJECTED` event. """
        self.processed = True
        self.valid = False
        self._emit_event(EventType.ACTION_REJECTED, **kwargs)

    def _emit_event(self, event_type, msg="", **kwargs):
        """ Emit an event indicating success or failure. """
        # Store msg for testing.
        self.msg = msg

        edata = kwargs.setdefault('event_data', {})
        edata['actor'] = self.actor
        edata['target'] = self.target
        edata['type'] = self.type.value
        # include action_data ?

        Event.emit(event_type, msg=msg, **kwargs)

    ### Alternate constructors ###

    @classmethod
    def from_dict(cls, data_dict):
        """  Build action from data_dict, ie from a json string. """
        d = data_dict.copy()
        try:
            type_ = ActionType(d.pop('type'))
        except ValueError as e:
            logger.warning(e)
            raise UnknownActionTypeError(e.args[0]) from e
        try:
            return cls(type=type_, **d)
        except TypeError as e:
            logger.warning(e)
            raise ActionDataError(e.args[0]) from e

    # Shortcuts for common action types

    @classmethod
    def attack(cls, a, t, d=None):
        """ Short hand constructor for an ATTACK actin. """
        return cls(ActionType.ATTACK, a, t, d)

    @classmethod
    def move(cls, a, d):
        """ Short hand constructor for a MOVE actin. """
        return cls(ActionType.MOVE, a, None, d)

    @classmethod
    def inflict_dmg(cls, a, t, d):
        """ Short hand constructor for an INFLICT_DMG actin. """
        return cls(ActionType.INFLICT_DMG, a, t, d)
