"""
barbarian.gamestates.py
=======================

Game state objects & their manager.

"""
import logging

from barbarian import libtcodpy as tcod
from barbarian import gui
from barbarian.input import common as input
from barbarian.renderers import renderer
from barbarian.utils import rng

logger = logging.getLogger(__name__)

class StateManager(object):

    """
    Main Controller.

    Stack-like container of state objects, holding pointer to the currently
    active one.

    blaaa

    """

    def __init__(self, initial_state=None):
        self._states = []

        if initial_state is not None:
            self._states.append(initial_state)

        logger.debug("State Manager Initialized with states %s", self._states)

    @property
    def current_state(self):
        """ Currently active state is the one sitting on top of the stack. """
        # TODO: Bettr error handling. Raise a specific exception if empty?
        return self._states[-1]

    @property
    def is_done(self):
        """ We'll be done when there are no more state objs on the stack. """
        # TODO: better name
        return not len(self._states) >= 1

    def pop(self):
        s = self._states.pop()
        logger.debug("State %s popped off the stack", s)
        logger.debug("Current State Stack: %s", self._states)

    def push(self, s):
        if self._states:
            self.current_state.next_state = None
        self._states.append(s)
        logger.debug("State %s pushed on the stack", self.current_state)
        logger.debug("Current State Stack: %s", self._states)

    def update(self):
        """ Main event loop. """
        self.current_state.update()
        self.current_state.render()

        renderer.flush()

        # Switch state if requested
        next_state = self.current_state.next_state
        if self.current_state.done:
            self.pop()
        if next_state is not None:
            self.push(next_state)

class GameState(object):

    """
    Base Game State.

    Implements requesting the state manager state for transitions, which will
    be needed by all state objects, and a few stub methods.

    """

    def __init__(self):
        self.done = False
        self.next_state = None

    def _pop(self):
        """ Signal the state manager to pop self. """
        self.done = True

    def _push(self, s):
        """ Signal to state manager to push s onto self. """
        self.next_state = s

    def _replace_with(self, s):
        """ Shortcut: pop self & push s, effectively replacing self with s. """
        self._pop()
        self._push(s)

    def update(self):
        """ Stub update method. No-op. """
        pass

    def render(self):
        """ Stub render method. No-op. """
        pass

    def process_input(self):
        """ Stub input processing method. No-op. """
        pass

    # event methods: on_init, on_leave, ...
    # => http://blog.nuclex-games.com/tutorials/cxx/game-state-management/

    # ...


### Dummy States ###
####################

class InitState(GameState):

    """ Game Initialization. """

    def update(self):
        renderer.init()
        self._replace_with(MainMenuState())

class ShutDownState(GameState):

    """ Cleanup on Shut-down. """

    def update(self):
        self._pop()

class MainMenuState(GameState):

    def update(self):
        k = input.collect_keypresses()
        if k is not None:
            # Rather push
            self._replace_with(DungeonState())

    def render(self):
        renderer.clear()
        renderer.dummy_main_menu()

class DungeonState(GameState):

    """ Dummy Gameplay State """

    def __init__(self):
        from barbarian.dungeon import Dungeon
        from barbarian.objects.factories import build_player

        self.dungeon = Dungeon()
        self.player = build_player(self.dungeon.current_level)

        super(DungeonState, self).__init__()

    def process_input(self):

        key  = input.collect_keypresses()
        gui.manager.process_input(key)  # TODO: assign retval to key

        action = input.check_keypress(key, 'std_state')

        if action == 'move_n':
            self.player.move(0, -1, self.dungeon.current_level)
        elif action == 'move_s':
            self.player.move(0, 1, self.dungeon.current_level)
        elif action == 'move_w':
            self.player.move(-1, 0, self.dungeon.current_level)
        elif action == 'move_e':
            self.player.move(1, 0, self.dungeon.current_level)
        elif action == 'move_ne':
            self.player.move(1, -1, self.dungeon.current_level)
        elif action == 'move_se':
            self.player.move(1, 1, self.dungeon.current_level)
        elif action == 'move_sw':
            self.player.move(-1, 1, self.dungeon.current_level)
        elif action == 'move_nw':
            self.player.move(-1, -1, self.dungeon.current_level)

        if key == '<ctrl>-m':
            gui.manager.msg(
                rng.choice(('foo', 'bar', 'baz', 'moop')),
                rng.choice(('red', 'white', 'green', 'gray'))
            )
        elif key == '<ctrl>-d':
            gui.manager.show_widget('debug_console')
        elif key == '<esc>':
            self._replace_with(ShutDownState())

    def update(self):
        self.process_input()
        self.dungeon.current_level.update()

    def render(self):
        renderer.clear()      # TODO: Clear only whats needed...
        renderer.dummy_draw_level(self.dungeon.current_level)
        renderer.dummy_draw_obj(self.player)
        gui.manager.render()

