import tcod

from ..utils import c_to_idx, closest_open_cell, path_to
from .. import constants


class CursorMixin:

    def __init__(self, cx=None, cy=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._start_x, self._start_y = cx, cy
        self.recompute_path = False

    @property
    def cursor_x(self):
        return self.client.cursor_x

    @cursor_x.setter
    def cursor_x(self, v):
        self.client.cursor_x = v

    @property
    def cursor_y(self):
        return self.client.cursor_y

    @cursor_y.setter
    def cursor_y(self, v):
        self.client.cursor_y = v

    @property
    def path_from_cursor(self):
        return self.client.path_from_cursor

    @path_from_cursor.setter
    def path_from_cursor(self, v):
        self.client.path_from_cursor = v

    def set_cursor_pos(self, x, y):
        if (x, y) != (self.cursor_x, self.cursor_y):
            if (constants.MAP_VIEWPORT_X <= x < constants.MAP_VIEWPORT_W and
                constants.MAP_VIEWPORT_Y <= y < constants.MAP_VIEWPORT_H
            ):
                self.cursor_x, self.cursor_y = x, y
                self.recompute_path = True
            else:
                self.cursor_x, self.cursor_y = None, None
                self.clear_path()

    def move_cursor(self, dx, dy):
        x, y = max(0, self.cursor_x + dx), max(0, self.cursor_y + dy)
        self.set_cursor_pos(x, y)

    def compute_path(self):

        self.clear_path()

        if None not in (self.cursor_x, self.cursor_y):
            gs = self.client.gamestate
            map_w, map_h = gs.map['width'], gs.map['height']
            pathmap = gs.map['pathmap']
            explored = gs.explored_cells

            cx, cy = closest_open_cell(
                self.cursor_x, self.cursor_y, map_w, map_h, pathmap,
                cost_modifier=lambda i, d: (d * 0.2 if explored[i] else d)
            )
            px, py = gs.player['pos']
            path = list(path_to(cx, cy, px, py, map_w, pathmap))
            while path and not explored[c_to_idx(*path[0], map_w)]:
                path.pop(0)
            self.path_from_cursor = path

        return self.path_from_cursor

    def clear_path(self):
        self.path_from_cursor.clear()

    def update(self):
        # We can't set a starting position in the constructor because client
        # if not set yet, so we wait until the first update call to do so.
        if (self._start_x, self._start_y) != (None, None):
            self.cursor_x, self.cursor_y = self._start_x, self._start_y
            self._start_x, self._start_y = None, None

        if self.recompute_path:
            self.compute_path()
            self.recompute_path = False

        return super().update()


class GameLogMixin:

    @property
    def gamelog(self):
        return self.client.gamelog

    def log_msg(self, m):
        self.gamelog.append((self.client.gamestate.tick, m))

    # FIXME: Hacky, and relies too much on knowing the internal
    # event structure (ie, we need an event type enum or mapping
    # on the client).
    def log_event(self, e):
        # Action failed, not initiated by the player
        if e['type'] == 'action_rejected':
            actor, target = e['data']['actor'], e['data']['target']
            if actor and 'actor' in actor and not actor['actor']['is_player']:
                return
            if target and 'actor' in target and not target['actor']['is_player']:
                return
        if (
            e['type'] == 'food_state_updated' and
            e['data']['state'] in ('full', 'satiated') and
            e['data']['previous_state'] in ('full',)
        ):
            return
        if e['msg']:
            self.log_msg(e['msg'])
        # else:
        #     print(f'cant process event: {e}')

    def log_error(self, r):
        errcode, msg = r.err_code, getattr(r, 'msg', None)
        if msg:
            m = f'%c%c%c%c[REQUEST ERROR: {errcode} - {msg}]%c'
            self.log_msg(
                m % (tcod.COLCTRL_FORE_RGB, 255, 1, 1, tcod.COLCTRL_STOP))
        else:
            print(r)


class BloodstainsMixin:

    @property
    def bloodstains(self):
        return self.client.bloodstains
