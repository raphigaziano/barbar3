"""
barbarian.gamestates.py
=======================

Game state objects & their manager.

TODO: UNITTESTME!

"""
from barbarian import libtcodpy as tcod
from barbarian import gui
from barbarian.renderers import renderer

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

    @property
    def current_state(self):
        """ Currently active state is the one sitting on top of the stack. """
        # TODO: Bettr error handling. Raise a specific exception ?
        return self._states[-1]

    @property
    def is_done(self):
        """ We'll be done when there are no more state objs on the stack. """
        # TODO: better name
        return not len(self._states) >= 1

    def pop(self):
        self._states.pop()

    def push(self, s):
        self._states.append(s)

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

    def update(self):
        renderer.init()
        self._replace_with(MainMenuState())

class ShutDownState(GameState):

    def update(self):
        self._pop()

class MainMenuState(GameState):

    def update(self):
        k = tcod.console_check_for_keypress(tcod.KEY_PRESSED)
        if k.vk is not tcod.KEY_NONE:
            self._replace_with(DungeonState())

    def render(self):
        renderer.dummy_main_menu()

class DungeonState(GameState):

    """ Dummy Gameplay State """

    def __init__(self):
        from mapgen import make_map
        from utils import rng

        self.m = make_map()

        self.px, self.py = rng.randrange(0, 80), rng.randrange(0, 40)
        while self.m.get_cell(self.px, self.py):
            self.px, self.py = rng.randrange(0, 80), rng.randrange(0, 40)

        super(DungeonState, self).__init__()
        renderer.clear()

    def process_input(self):

        key = tcod.console_check_for_keypress(tcod.KEY_PRESSED)

        gui.manager.process_input(key)

        # if key.vk is not tcod.KEY_NONE:
        #     self.dbgcons.add_msg('[DEBUG] key %c was pressed' % key.c)

        if key.vk in (tcod.KEY_UP, tcod.KEY_KP8):
            self.py -= 1
            gui.manager.debug('[DEBUG] moovinUP', 'red')
        elif key.vk in (tcod.KEY_DOWN, tcod.KEY_KP2):
            self.py += 1
            gui.manager.debug('[DEBUG] goinDOWN', 'red')
        elif key.vk in (tcod.KEY_LEFT, tcod.KEY_KP4):
            self.px -= 1
            gui.manager.debug('[DEBUG] goleft', 'red')
        elif key.vk in (tcod.KEY_RIGHT, tcod.KEY_KP6):
            self.px += 1
            gui.manager.debug('[DEBUG] gright', 'red')
        elif key.c == ord('m'):
            from barbarian.utils import rng
            gui.manager.msg(
                rng.choice(('foo', 'bar', 'baz', 'moop')),
                rng.choice(('red', 'white', 'green', 'gray'))
            )
        elif key.c == ord('d'):
            gui.manager.show_widget('debug_console')
        elif key.vk == tcod.KEY_ESCAPE:
            self._replace_with(ShutDownState())

    def update(self):
        self.process_input()

    def render(self):
        renderer.clear()      # TODO: Clear only whats needed...
        renderer.dummy_draw_map(self.m)
        renderer.dummy_draw_player(self.px, self.py)
        gui.manager.render()

