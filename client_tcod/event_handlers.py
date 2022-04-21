"""
Tcod event processing.

"""
from string import ascii_lowercase

from .nw import Request
from . import constants
from .utils import c_to_idx
from .constants import (
    VI_KEYS, MOVE_KEYS,
    MAP_VIEWPORT_X, MAP_VIEWPORT_Y, MAP_VIEWPORT_W, MAP_VIEWPORT_H)

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
            confirm = not e.mod & tcod.event.KMOD_SHIFT
            return self.quit(confirm)

    def quit(self, confirm=True):
        from .modes.ui import PromptConfirmMode
        if confirm:
            confirm = PromptConfirmMode(
                title='Quit',
                txt='Are you sure you want to quit?',
                on_leaving=lambda _: self.mode.pop()
            )
            self.mode.push(confirm)
        else:
            self.mode.pop()

    def handle(self, ctxt):
        """ Process UI events. """
        # TODO: yield to allow several request sends ?
        for e in tcod.event.get():
            r = self.dispatch(e)
            if r:
                return r


class CursorPositionMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_mouse_pos = None

    def get_mouse_state(self, ctxt):
        ms = tcod.event.get_mouse_state()
        ctxt.convert_event(ms)
        return ms

    def handle(self, ctxt):

        ms = self.get_mouse_state(ctxt)

        if self.last_mouse_pos is None:
            # Cursor not intialized yet
            if ms.tile == (0, 0):
                return super().handle(ctxt)
            self.last_mouse_pos = ms.tile

        if self.last_mouse_pos != ms.tile:
            self.mode.set_cursor_pos(ms.tile.x, ms.tile.y)
            self.last_mouse_pos = ms.tile

        return super().handle(ctxt)

    def cursor_cmds(self, e):

        if e.sym in MOVE_KEYS:
            dx, dy = MOVE_KEYS[e.sym]
            if e.mod & tcod.event.KMOD_SHIFT:
                dx, dy = dx * 5, dy * 5
            self.mode.move_cursor(dx, dy)

    def ev_mousebuttondown(self, e):
        from .modes.run import MoveToMode
        self.mode.replace_with(MoveToMode(path=self.mode.compute_path()))


class DebugEventsMixin:

    def debug_events(self, e):

        if (e.mod & tcod.event.KMOD_ALT and e.sym == tcod.event.K_n):
            return Request.action('change_level')

        if (e.mod & tcod.event.KMOD_ALT and e.sym == tcod.event.K_r):
            from .modes.ui import DbgMapMode    # Avoid circular import
            return self.mode.push(DbgMapMode())

        if (e.mod & tcod.event.KMOD_ALT and e.sym == tcod.event.K_d):
            constants.MAP_DEBUG = not constants.MAP_DEBUG
            return Request.set('MAP_DEBUG', val=constants.MAP_DEBUG)

        if (e.mod & tcod.event.KMOD_ALT and e.sym == tcod.event.K_i):
            v = not constants.SHOW_DEBUG_INFO
            return self.mode.setvar_g('SHOW_DEBUG_INFO', v)

        if (e.mod & tcod.event.KMOD_ALT and e.sym == tcod.event.K_x):
            v = not constants.SHOW_UNEXPLORED_CELLS
            return self.mode.setvar_g('SHOW_UNEXPLORED_CELLS', v)

        if (e.mod & tcod.event.KMOD_ALT and e.sym == tcod.event.K_p):
            v = not constants.SHOW_PATH_INFO
            return self.mode.setvar_g('SHOW_PATH_INFO', v)

        if (e.mod & tcod.event.KMOD_ALT and e.sym == tcod.event.K_v):
            v = not constants.SHOW_SPAWN_ZONES
            return self.mode.setvar_g('SHOW_SPAWN_ZONES', v)

        if (e.mod & tcod.event.KMOD_ALT and e.sym == tcod.event.K_f):
            v = not constants.IGNORE_FOV
            return self.mode.setvar_g('IGNORE_FOV', v)

        return False


class RunEventHandler(
        DebugEventsMixin, CursorPositionMixin, BaseEventHandler):
    """ Main hander, used for for actual game commands """

    def ev_keydown(self, e):
        from .modes.ui import HelpModalMode, TargetMode
        from .modes.run import MoveToMode

        if e.sym == tcod.event.K_ESCAPE:
            if self.mode.path_from_cursor:
                return self.mode.clear_path()

        if (r := super().ev_keydown(e)):
            return r

        # Explicit check: None can be returned to the called, but not False
        # (Used to indicate a no-op)
        if (r := super().debug_events(e)) != False:
            return r

        if (e.mod & tcod.event.KMOD_SHIFT and e.sym == tcod.event.K_COMMA):
            return self.mode.push(HelpModalMode())

        if (e.mod & tcod.event.KMOD_SHIFT and e.sym == tcod.event.K_m):
            return self.mode.show_message_log()

        if e.sym in MOVE_KEYS:
            if e.mod & tcod.event.KMOD_SHIFT:
                return self.mode.move_r({'dir': MOVE_KEYS[e.sym]})
            else:
                return Request.action('move', {'dir': MOVE_KEYS[e.sym]})

        if e.sym in (tcod.event.K_SEMICOLON, tcod.event.K_KP_5):
            if e.mod & tcod.event.KMOD_SHIFT:
                return self.mode.rest_r()
            else:
                return Request.action('idle')

        if e.sym in (tcod.event.K_COMMA, tcod.event.K_g):
            return self.mode.get_item()
        if e.sym == tcod.event.K_d:
            return self.mode.drop_item()

        if e.sym == tcod.event.K_w:
            if e.mod & tcod.event.KMOD_SHIFT:
                return self.mode.wear_item()
            else:
                return self.mode.wield_item()

        if e.sym == tcod.event.K_e:
            return self.mode.eat()

        if (e.mod & tcod.event.KMOD_CTRL and e.sym == tcod.event.K_o):
            return self.mode.open_door()
        if (e.mod & tcod.event.KMOD_CTRL and e.sym == tcod.event.K_c):
            return self.mode.close_door()

        if e.sym == tcod.event.K_LESS:
            if e.mod & tcod.event.KMOD_SHIFT:
                use_key = 'down'
            else:
                use_key = 'up'
            return Request.action('use_prop', {'use_key': use_key})

        if e.sym == tcod.event.K_x:
            px, py = self.mode.client.gamestate.player['pos']
            self.mode.clear_path()
            return self.mode.push(
                TargetMode(
                    px, py, on_leaving=lambda m:
                        self.mode.push(MoveToMode(path=m.path_from_cursor))
            ))
        if e.sym in (tcod.event.K_RETURN, tcod.event.K_KP_ENTER):
            if self.mode.path_from_cursor:
                return self.mode.push(MoveToMode(path=self.mode.path_from_cursor))
        if e.sym == tcod.event.K_TAB:
            if self.mode.client.closest_actors:
                return self.mode.push(
                    TargetMode(
                        entity_list=self.mode.client.closest_actors,
                        on_leaving=lambda m:
                            self.mode.push(MoveToMode(path=m.path_from_cursor))
                ))

        if e.sym == tcod.event.K_o:
            return self.mode.autoxplore()

        if e.sym == tcod.event.K_i:
            self.mode.show_inventory()

    def ev_mousebuttondown(self, e):
        from .modes.run import MoveToMode
        self.mode.push(MoveToMode(path=self.mode.compute_path()))


class TargetingEventHandler(CursorPositionMixin, BaseEventHandler):

    def ev_keydown(self, e):

        if e.sym == tcod.event.K_ESCAPE:
            self.mode.pop()

        super().cursor_cmds(e)

        if e.sym in (tcod.event.K_RETURN, tcod.event.K_KP_ENTER):
            self.mode.confirm()
            self.mode.pop()

        if e.sym == tcod.event.K_TAB:
            self.mode.target_next_entity()


class MoveToEventHandler(CursorPositionMixin, BaseEventHandler):
    pass


class DbgMapEventHandler(DebugEventsMixin, BaseEventHandler):

    def ev_keydown(self, e):

        if e.sym == tcod.event.K_ESCAPE:
            return self.mode.pop()

        if r := super().ev_keydown(e):
            return r

        # Call it *before* super().debug_cmds,to shadow its Alt-r event
        if (e.mod & tcod.event.KMOD_ALT and e.sym == tcod.event.K_r):
            self.mode.running = not self.mode.running
            return

        if (e.sym == tcod.event.K_LEFT):
            self.mode.running = False
            self.mode.set_map_index(-1)
        if (e.sym == tcod.event.K_RIGHT):
            self.mode.running = False
            self.mode.set_map_index(1)

        if r := super().debug_events(e):
            return r


class GameOverEventHandler(BaseEventHandler):

    def ev_keydown(self, e):

        if r := super().ev_keydown(e):
            return r

        if e.sym == tcod.event.K_n:
            return self.mode.client.start(None)


class BaseUIModalEventHandler(BaseEventHandler):

    def ev_keydown(self, e):

        if e.sym == tcod.event.K_ESCAPE:
            self.mode.pop()


class PagedModalEventHandler(BaseUIModalEventHandler):

    def ev_keydown(self, e):

        super().ev_keydown(e)

        if e.sym in (tcod.event.K_DOWN, tcod.event.K_KP_2, tcod.event.K_j):
            if e.mod & tcod.event.KMOD_SHIFT:
                self.mode.set_offset(10)
            else:
                self.mode.set_offset(1)
        if e.sym in (tcod.event.K_UP, tcod.event.K_KP_8, tcod.event.K_k):
            if e.mod & tcod.event.KMOD_SHIFT:
                self.mode.set_offset(-10)
            else:
                self.mode.set_offset(-1)

        if e.sym in (tcod.event.K_PAGEDOWN,):
            self.mode.set_offset(10)
        if e.sym in (tcod.event.K_PAGEUP,):
            self.mode.set_offset(-10)
        if e.sym in (tcod.event.K_END,):
            self.mode.offset = self.mode.max_offset
        if e.sym in (tcod.event.K_HOME,):
            self.mode.offset = 0


class PromptConfirmEventHandler(BaseUIModalEventHandler):

    def ev_keydown(self, e):

        super().ev_keydown(e)

        if e.sym == tcod.event.K_y:
            self.mode.confirm()

        self.mode.pop()


class PromptDirectionEventHandler(BaseUIModalEventHandler):

    def ev_keydown(self, e):

        super().ev_keydown(e)

        if (dir_ := MOVE_KEYS.get(e.sym, None)):
            if dir_ == (0, 0):
                return
            dx, dy = dir_
            self.mode.set_callback_kwargs('on_leaving', {'dx': dx, 'dy': dy})
            self.mode.pop()


class MenuEventHandler(BaseUIModalEventHandler):

    def ev_keydown(self, e):

        super().ev_keydown(e)

        if (dir_ := MOVE_KEYS.get(e.sym, None)):
            if not (e.sym in VI_KEYS and
                    not e.mod & tcod.event.KMOD_SHIFT):
                self.mode.set_cursor(dir_)
                return

        if e.sym == tcod.event.K_RETURN:
            self.mode.select_option()

        try:
            # Maj key is ignored, so sym should always be lowercase
            if chr(e.sym) in ascii_lowercase:
                idx = e.sym - 97
                self.mode.select_option(idx)
        except ValueError:
            pass
