"""
Tcod event processing.

"""
from .nw import Request
from . import constants
from .constants import MOVE_KEYS

import tcod.event


class BaseEventHandler(tcod.event.EventDispatch[None]):
    """ Base handler to process common events. """

    def __init__(self, game_mode, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = game_mode

    def ev_quit(self, e: tcod.event.Quit) -> dict:
        return self.quit()

    def ev_keydown(self, e: tcod.event.KeyDown) -> dict:

        if e.sym == tcod.event.K_ESCAPE:
            return self.quit()

    def quit(self):
        from .modes.ui import PromptConfirmMode
        confirm = PromptConfirmMode(
            prompt='Are you sure you want to quit?',
            on_leaving=lambda _: self.mode.pop()
        )
        self.mode.push(confirm)

    def handle(self, ctxt):
        """ Process UI events. """
        for e in tcod.event.get():
            ctxt.convert_event(e)
            return self.dispatch(e)


class DebugEventsMixin:

    def debug_events(self, e):

        if (e.mod & tcod.event.KMOD_LALT and e.sym == tcod.event.K_n):
            return Request.action('change_level')

        if (e.mod & tcod.event.KMOD_LALT and e.sym == tcod.event.K_r):
            from .modes.ui import DbgMapMode    # Avoid circular import
            return self.mode.push(DbgMapMode())

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


class RunEventHandler(DebugEventsMixin, BaseEventHandler):
    """ Main hander, used for for actual game commands """

    def ev_keydown(self, e):

        if r := super().ev_keydown(e):
            return r

        if r := super().debug_events(e):
            return r

        if e.sym in MOVE_KEYS:
            if e.mod & tcod.event.KMOD_LSHIFT:
                return Request.client('move_r', {'dir': MOVE_KEYS[e.sym]})
            else:
                return Request.action('move', {'dir': MOVE_KEYS[e.sym]})

        if e.sym in (tcod.event.K_COMMA, tcod.event.K_KP_5):
            return Request.action('idle')

        if e.sym in (tcod.event.K_SEMICOLON, tcod.event.K_g):
            return Request.action('get_item')
        if e.sym == tcod.event.K_d:
            return Request.action('drop_item')

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


class DbgMapEventHandler(DebugEventsMixin, BaseEventHandler):

    def ev_keydown(self, e):

        if r := super().ev_keydown(e):
            return r

        # Call it *before* super().debug_cmds,to shadow its Alt-r event
        if (e.mod & tcod.event.KMOD_LALT and e.sym == tcod.event.K_r):
            return Request.client('setvar', {'key': 'mapgen_index', 'val': 0})

        if r := super().debug_events(e):
            return r


class GameOverEventHandler(BaseEventHandler):

    def ev_keydown(self, e):

        if r := super().ev_keydown(e):
            return r

        if e.sym == tcod.event.K_n:
            return Request.client('start')


class BasePromptEventHandler(BaseEventHandler):

    def ev_keydown(self, e):

        if e.sym == tcod.event.K_ESCAPE:
            self.mode.pop()


class PromptConfirmEventHandler(BasePromptEventHandler):

    def ev_keydown(self, e):

        super().ev_keydown(e)

        if e.sym == tcod.event.K_y:
            self.mode.confirm()

        self.mode.pop()


class PromptDirectionEventHandler(BasePromptEventHandler):

    def ev_keydown(self, e):

        super().ev_keydown(e)

        if e.sym in MOVE_KEYS:
            dir_ = MOVE_KEYS[e.sym]
            if dir_ == (0, 0):
                return
            dx, dy = dir_
            self.mode.set_callback_kwargs('on_leaving', {'dx': dx, 'dy': dy})
            self.mode.pop()
