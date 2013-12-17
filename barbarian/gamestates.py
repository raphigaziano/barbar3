import libtcodpy as tcod


class StateManager(object):

    def __init__(self):
        self._states = []
        self._next_state = None

    @property
    def current_state(self):
        return self._states[-1]

    def pop(self):
        self._states.pop()

    def push(self, s):
        self._next_state = s

    def update(self):
        if self._next_state:
            self._states.append(self._next_state)
            self._next_state = None


class GameState(object):

    def process_input():
        pass

    # ...


class DungeonState(GameState):

    def __init__(self):
        import map
        from utils import rng

        self.m = map.Map(80, 40, map.dummy_generator())

        self.px, self.py = rng.randrange(0, 80), rng.randrange(0, 40)
        while self.m.get_cell(self.px, self.py):
            self.px, self.py = rng.randrange(0, 80), rng.randrange(0, 40)

    def process_input(self):

        key = tcod.console_check_for_keypress(tcod.KEY_PRESSED)

        if key.vk in (tcod.KEY_UP, tcod.KEY_KP8):
            self.py -= 1
        elif key.vk in (tcod.KEY_DOWN, tcod.KEY_KP2):
            self.py += 1
        elif key.vk in (tcod.KEY_LEFT, tcod.KEY_KP4):
            self.px -= 1
        elif key.vk in (tcod.KEY_RIGHT, tcod.KEY_KP6):
            self.px += 1
        elif key.vk == tcod.KEY_ESCAPE:
            pass # How to we break the outside loop ?

