"""
Tcod event processing.

"""
from .nw import Request
from . import constants

import tcod.event


class BaseEventHandler(tcod.event.EventDispatch[None]):
    """ Base handler to process common events. """

    def ev_quit(self, e: tcod.event.Quit) -> dict:
        return Request.client('shutdown')

    def ev_keydown(self, e: tcod.event.KeyDown) -> dict:

        if e.sym == tcod.event.K_ESCAPE:
            return Request.client('shutdown')

    def debug_events(self, e):

        if (e.mod & tcod.event.KMOD_LALT and e.sym == tcod.event.K_n):
            return Request.action('change_level')

        if (e.mod & tcod.event.KMOD_LALT and e.sym == tcod.event.K_r):
            from .modes.ui import DbgMapMode    # Avoid circular import
            return Request.client('push_mode', {'new_mode': DbgMapMode})

        if (e.mod & tcod.event.KMOD_LALT and e.sym == tcod.event.K_d):
            constants.MAP_DEBUG = not constants.MAP_DEBUG
            return Request.set('MAP_DEBUG', val=constants.MAP_DEBUG)

        if (e.mod & tcod.event.KMOD_LALT and e.sym == tcod.event.K_x):
            v = not constants.SHOW_UNEXPLORED_CELLS
            return Request.client(
                'setvar_g', {'key': 'SHOW_UNEXPLORED_CELLS', 'val': v})

        if (e.mod & tcod.event.KMOD_LALT and e.sym == tcod.event.K_p):
            v = not constants.SHOW_PATH_INFO
            return Request.client(
                'setvar_g', {'key': 'SHOW_PATH_INFO', 'val': v})

        if (e.mod & tcod.event.KMOD_LALT and e.sym == tcod.event.K_v):
            v = not constants.SHOW_SPAWN_ZONES
            return Request.client(
                'setvar_g', {'key': 'SHOW_SPAWN_ZONES', 'val': v})

        if (e.mod & tcod.event.KMOD_LALT and e.sym == tcod.event.K_f):
            v = not constants.IGNORE_FOV
            return Request.client(
                'setvar_g', {'key': 'IGNORE_FOV', 'val': v})

    def handle(self, ctxt):
        """ Process UI events. """
        for e in tcod.event.get():
            ctxt.convert_event(e)
            return self.dispatch(e)


class RunEventHandler(BaseEventHandler):
    """ Main hander, used for for actual game commands """

    MOVE_KEYS = {  # key_symbol: (x, y)
        # Arrow keys.
        tcod.event.K_LEFT: (-1, 0),
        tcod.event.K_RIGHT: (1, 0),
        tcod.event.K_UP: (0, -1),
        tcod.event.K_DOWN: (0, 1),
        tcod.event.K_HOME: (-1, -1),
        tcod.event.K_END: (-1, 1),
        tcod.event.K_PAGEUP: (1, -1),
        tcod.event.K_PAGEDOWN: (1, 1),
        tcod.event.K_PERIOD: (0, 0),
        # Numpad keys.
        tcod.event.K_KP_1: (-1, 1),
        tcod.event.K_KP_2: (0, 1),
        tcod.event.K_KP_3: (1, 1),
        tcod.event.K_KP_4: (-1, 0),
        tcod.event.K_KP_6: (1, 0),
        tcod.event.K_KP_7: (-1, -1),
        tcod.event.K_KP_8: (0, -1),
        tcod.event.K_KP_9: (1, -1),
        tcod.event.K_CLEAR: (0, 0),  # Numpad `clear` key.
        # Vi Keys.
        tcod.event.K_h: (-1, 0),
        tcod.event.K_j: (0, 1),
        tcod.event.K_k: (0, -1),
        tcod.event.K_l: (1, 0),
        tcod.event.K_y: (-1, -1),
        tcod.event.K_u: (1, -1),
        tcod.event.K_b: (-1, 1),
        tcod.event.K_n: (1, 1),
    }

    def ev_keydown(self, e):

        if r := super().ev_keydown(e):
            return r

        if r := super().debug_events(e):
            return r

        if e.sym in self.MOVE_KEYS:
            if e.mod & tcod.event.KMOD_LSHIFT:
                return Request.client('move_r', {'dir': self.MOVE_KEYS[e.sym]})
            else:
                return Request.action('move', {'dir': self.MOVE_KEYS[e.sym]})

        if e.sym in (tcod.event.K_COMMA, tcod.event.K_KP_5):
            return Request.action('idle')

        if (e.mod & tcod.event.KMOD_LCTRL and e.sym == tcod.event.K_o):
            return Request.client('open_door')
        if (e.mod & tcod.event.KMOD_LCTRL and e.sym == tcod.event.K_c):
            return Request.client('close_door')

        if e.sym == tcod.event.K_LESS:
            if e.mod & tcod.event.KMOD_LSHIFT:
                use_key = 'down'
            else:
                use_key = 'up'
            return Request.action('use_prop', {'use_key': use_key})

        if (e.mod & tcod.event.KMOD_LCTRL and e.sym == tcod.event.K_x):
            return Request.client('autoxplore')

        if e.sym == tcod.event.K_i:
            return Request.action('INVALID LOL')

    # def ev_mousemotion(self, ev):
    #     print(ev)


class DbgMapEventHandler(BaseEventHandler):

    def ev_keydown(self, e):

        if r := super().ev_keydown(e):
            return r

        # Call it *before* super().debug_cmds,to shadow its Alt-r event
        if (e.mod & tcod.event.KMOD_LALT and e.sym == tcod.event.K_r):
            return Request.client(
                'setvar', {'key': 'mapgen_index', 'val': 0})

        if r := super().debug_events(e):
            return r


class GameOverEventHandler(BaseEventHandler):

    def ev_keydown(self, e):

        if r := super().ev_keydown(e):
            return r

        if e.sym == tcod.event.K_n:
            return Request.client('start')


class PromptDirectionEventHandler(BaseEventHandler):

    def ev_keydown(self, e):

        if e.sym == tcod.event.K_ESCAPE:
            return Request.client('pop_mode')

        # FIXME: move those to constants
        if e.sym in RunEventHandler.MOVE_KEYS:
            dir_ = RunEventHandler.MOVE_KEYS[e.sym]
            if dir_ != (0, 0):
                return dir_
