"""
Game modes.

Modes are really statesn handlind by a classic state machine.
We're calling them modes here both as a nod to Vi and (mostly) to
avoid confusion with gamestate.

"""
import logging

from .. import constants
from ..event_handlers import BaseEventHandler, GameOverEventHandler


# set up logging to console
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)

logger = logging.getLogger(__name__)
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

    @property
    def done(self):
        return not self._modes

    def pop(self):
        # Make sure to call leave cb *after* we've popped its mode.
        # This callback will probably often trigger another mode change, 
        # which should be handled by its caller mode.
        popped = self._modes.pop()
        popped.on_leaving()
        logger.debug("Mode %s popped off the stack", popped)
        logger.debug("Current Mode Stack: %s", self._modes)
        # - if self._modes:
        # -     self.current_mode.on_revealed()

    def push(self, new_mode):
        if self._modes:
            self.current_mode.next_mode = None
            # - self.current_mode.on_obscured()
        new_mode.client = self.client
        self._modes.append(new_mode)
        logger.debug("Mode %s pushed on the stack", self.current_mode)
        logger.debug("Current Mode Stack: %s", self._modes)

    def update(self):

        # Switch mode if requested

        # We nedd to grab the next mode now to handle replacement
        # (current_mode will break once it's been popped).
        next_mode = self.current_mode.next_mode
        if self.current_mode.done:
            self.pop()
        if next_mode is not None:
            self.push(next_mode)

        if not self.done:
            # Let the current mode do its thing
            return self.current_mode.update()


class BaseGameMode:
    """ Base Mode class. """

    event_handler_cls = BaseEventHandler

    def __init__(
        self,
        on_entered=None, on_leaving=None,
        on_revealed=None, on_obscured=None,
    ):
        self.client = None
        self.event_handler = self.event_handler_cls(self)

        self.done = False
        self.next_mode = None

        self._bind(on_entered, '_cb_on_entered')
        self._bind(on_leaving, '_cb_on_leaving')
        # self._bind(on_revealed, '_cb_on_revealed')
        # self._bind(on_obscured, '_cb_on_obscured')

    # --- Callback ---

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

    def set_callback_kwargs(self, cb_name, kwargs):
        setattr(self, f'_cb_{cb_name}_kwargs', kwargs)

    def on_entered(self):
        return self.callback('_cb_on_entered')

    def on_leaving(self):
        return self.callback('_cb_on_leaving')

    # --- Fsm management ---

    def pop(self):
        """ Signal the Mode manager to pop self. """
        self.done = True

    def push(self, next_mode):
        """ Signal the Mode manager to push s onto self. """
        self.next_mode = next_mode

    def replace_with(self, next_mode):
        """
        Shortcut: pop self & push next_mode, effectively replacing self 
        with next_mode.

        """
        self.pop()
        self.push(next_mode)

    # --- Mode run ---

    def setvar(self, k, v):
        setattr(self, k, v)
        print(f"{k}: {getattr(self, k)}")

    def setvar_g(self, k, v):
        setattr(constants, k, v)
        print(f"{k}: {getattr(constants, k)}")

    def update(self):
        return self.event_handler.handle(self.client.context)

    def process_response(self, r):
        pass    # No-op

    def render(self, gamestate, renderer):
        pass    # No-op


class InitMode(BaseGameMode):
    """
    No-op init mode.

    May become useful, but mostly used for testing mode handling for now.

    """

    def update(self):
        from .run import RunMode
        self.replace_with(RunMode())


class GameOverMode(BaseGameMode):

    event_handler_cls = GameOverEventHandler

    def render(self, gs, renderer):
        renderer.render_gameover_screen(gs)
