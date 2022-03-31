"""
Game events handling.

"""
from enum import auto
from dataclasses import dataclass, field

import logging

from barbarian.utils.types import StringAutoEnum


logger = logging.getLogger(__name__)


class EventType(StringAutoEnum):

    ACTION_ACCEPTED = auto()
    ACTION_REJECTED = auto()
    ACTOR_SPOTTED = auto()
    ACTOR_DIED = auto()
    ENTITY_CONSUMED = auto()
    FOOD_STATE_UPDATED = auto()


@dataclass()
class Event:
    """
    Game event & event manager via class methods.

    A game event represent something that happened in the game, and
    to which various systems (or the client) can react. They differ
    from `barbarian.action.Action`, in that even though they may
    trigger some other actions, they're used to represent a deed's
    results, rather than its intent (which is what Actions are for).

    Events are stored both in a queue, (polled by internal systems) and
    in a log (sent to the client, and which may decide to keep track
    of some milestone events).

    Event flags:

        - `processed`: Polling systems should set this flag to True
          once they're done with an event to avoid reprocessing it.
        - `transient`: Most events are only relevent to track for the
          current turn (for instance, we d'ont really care about the
          results of actions once we've moved on to the next turn).
          Having this flag set to True (the default) means the event
          won't be kept in the log. Set it to False if you want to
          store it for longer.

    """

    _QUEUE = []
    _LOG = {}

    type: EventType
    msg: str = ''
    data: dict = field(default_factory=dict)

    processed: bool = False
    transient: bool = True
    internal: bool = False      # Not used right now

    @classmethod
    def emit(cls, *args, **kwargs):
        """ Create an event with the passed arguments and store it """
        kwargs['data'] = kwargs.pop('event_data', {}) or kwargs.pop('data', {})
        e = cls(*args, **kwargs)
        cls._QUEUE.append(e)
        cls._LOG.setdefault('current', []).append(e)
        return e

    @classmethod
    @property
    def queue(cls):
        return cls._QUEUE

    @classmethod
    def clear_queue(cls):
        logger.debug('Clearing %d events from the queue', len(cls._QUEUE))
        cls._QUEUE.clear()

    @classmethod
    def flush_log(cls, tick):
        """
        Clear current events from the log, and re-store the non-transient
        ones, using the current tick as an index.

        """
        current_events = cls._get_current()
        if not current_events:
            return

        filtered = [e for e in current_events if not e.transient]
        if filtered:
            cls._LOG[tick] = filtered

        logger.debug('Events logged for turn %d: %d', tick, len(current_events))
        current_events.clear()

    @classmethod
    def _get_current(cls):
        return cls._LOG.get('current', [])

    @classmethod
    def get_current_events(cls, current_tick, flush=False):
        """
        Return events logged for the current turn, and flush the log
        if requested.

        """
        events = cls._get_current()[:]
        if flush:
            cls.flush_log(current_tick)
        return events

    def serialize(self):
        return {
            'type': self.type.value,
            'msg': self.msg,
            'data': {
                k: v.serialize() if hasattr(v, 'serialize') else v
                for k, v in self.data.items()
            },
        }
