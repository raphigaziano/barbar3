"""
Game modes.

Modes are really statesn handlind by a classic state machine.
We're calling them modes here both as a nod to Vi and (mostly) to
avoid confusion with gamestate.

"""
import logging

from .. import constants
from ..ui_events import BaseEventHandler, GameOverEventHandler


# set up logging to console
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(console)
logger.setLevel(logging.INFO)


class ModeManager():
    """
    Store game modes and handle pushing / popping them on the stack.

    Defer commands to the currently runnnig mode.

    """
    def __init__(self, client):
        self.client = client
        self._modes = []

    @property
    def current_mode(self):
        """ Currently active mode is the one sitting on top of the stack. """
        # TODO: Bettr error handling. Raise a specific exception if empty?
        return self._modes[-1]

    def pop(self):
        popped = self._modes.pop()
        popped.callback('on_leaving')
        logger.debug("Mode %s popped off the stack", popped)
        logger.debug("Current Mode Stack: %s", self._modes)
        # - if self._modes:
        # -     self.current_mode.on_revealed()

    def push(self, mode_cls, **mode_kwargs):
        if self._modes:
            self.current_mode.next_mode = None
            # - self.current_mode.on_obscured()
        new_mode = mode_cls(self.client, **mode_kwargs)
        self._modes.append(new_mode)
        logger.debug("Mode %s pushed on the stack", self.current_mode)
        logger.debug("Current Mode Stack: %s", self._modes)

    def update(self, client):

        # Switch mode if requested

        # We nedd to grab the next mode now to handle replacement
        # (current_mode will break once it's been popped).
        next_mode = self.current_mode.next_mode
        next_mode_kwargs = self.current_mode.next_mode_kwargs
        if self.current_mode.done:
            self.pop()
        if next_mode is not None:
            self.push(next_mode, **next_mode_kwargs)

        # Let the current mode do its thing
        return self.current_mode.update(client.context)


class BaseGameMode:
    """ Base Mode class. """

    ui_events = BaseEventHandler()

    def __init__(
        self, client,
        on_entered=None, on_leaving=None,
        on_revealed=None, on_obscured=None,
        *args, **kwargs
    ):
        self.client = client
        self.done = False
        self.next_mode = None
        self.next_mode_kwargs = None

        self._bind(on_entered, 'on_entered')
        self._bind(on_leaving, 'on_leaving')
        # self._bind(on_revealed, 'on_revealed')
        # self._bind(on_obscured, 'on_obscured')

    def _bind(self, f, as_name):
        """ https://gist.github.com/hangtwenty/a928b801ca5c7705e94e """
        if f is None:
            f = lambda s, *args, **kwargs: None
        setattr(self, as_name, f.__get__(self, self.__class__))
        setattr(self, f'{as_name}_kwargs', {})

    def callback(self, cb_name):
        cb = getattr(self, cb_name)
        kwargs = getattr(self, f'{cb_name}_kwargs')
        return cb(**kwargs)

    def pop(self):
        """ Signal the Mode manager to pop self. """
        self.done = True

    def push(self, next_mode, **mode_kwargs):
        """ Signal the Mode manager to push s onto self. """
        self.next_mode = next_mode
        self.next_mode_kwargs = mode_kwargs

    def replace_with(self, next_mode, **mode_kwargs):
        """ Shortcut: pop self & push s, effectively replacing self with s. """
        self.pop()
        self.push(next_mode, **mode_kwargs)

    # mode command handlers: allow event handler to trigger a mode
    # change.

    def cmd_push_mode(self, data):
        new_mode = data['new_mode']
        new_mode_kwargs = data.get('kwargs', {})
        self.push(new_mode, **new_mode_kwargs)

    def cmd_pop_mode(self, data):
        self.pop()

    def cmd_replace_mode_with(self, data):
        new_mode = data['new_mode']
        new_mode_kwargs = data.get('kwargs', {})
        self.replace_with(new_mode, **new_mode_kwargs)

    def cmd_setvar(self, data):
        k, v = data['key'], data['val']
        setattr(self, k, v)
        print(f"{k}: {getattr(self, k)}")

    def cmd_setvar_g(self, data):
        k, v = data['key'], data['val']
        setattr(constants, k, v)
        print(f"{k}: {getattr(constants, k)}")

    def update(self, context):
        return self.ui_events.handle(context)

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


class InitMode(BaseGameMode):
    """
    No-op init mode.

    May become useful, but mostly used for testing mode handling for now.

    """

    def update(self, _):
        from .run import RunMode
        self.replace_with(RunMode)


class GameOverMode(BaseGameMode):
    ui_events = GameOverEventHandler()

    def render(self, gs, renderer):
        renderer.render_gameover_screen(gs)
