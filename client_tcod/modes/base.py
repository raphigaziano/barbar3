"""
Game modes.

Modes are really statesn handlind by a classic state machine.
We're calling them modes here both as a nod to Vi and (mostly) to
avoid confusion with gamestate.

"""
from .. import constants
from ..ui_events import BaseEventHandler


class BaseGameMode:
    """ Base Mode class. """

    def __init__(self, client):
        self.client = client
        self.ui_events = BaseEventHandler()

    def cmd_setvar(self, data):
        k, v = data['key'], data['val']
        setattr(self, k, v)
        print(f"{k}: {getattr(self, k)}")

    def cmd_setvar_g(self, data):
        k, v = data['key'], data['val']
        setattr(constants, k, v)
        print(f"{k}: {getattr(constants, k)}")

    def process_request(self, r):
        cmd = r['data'].pop('cmd')
        handler = getattr(self, f"cmd_{cmd}", None)
        if handler:
            handler(r['data'])
        else:
            print(f'No handler for command type {cmd}')

    def process_response(self, r):
        pass    # No-op

    def render(self, gamestate, renderer):
        pass    # No-op
