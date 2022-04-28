from copy import deepcopy

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

    @property
    def targeted_entity(self):
        return self.client.targeted_entity

    @targeted_entity.setter
    def targeted_entity(self, v):
        self.client.targeted_entity = v

    def _in_bounds(self, x, y, rect_x, rect_y, rect_w, rect_h):
        return (
            rect_x <= x < (rect_x + rect_w) and
            rect_y <= y < (rect_y + rect_h)
        )

    def set_cursor_pos(self, x, y):
        if (x, y) != (self.cursor_x, self.cursor_y):
            if self._in_bounds(
                    x, y,
                    constants.MAP_VIEWPORT_X, constants.MAP_VIEWPORT_Y,
                    constants.MAP_VIEWPORT_W, constants.MAP_VIEWPORT_H
            ):
                self.cursor_x, self.cursor_y = x, y
                self.recompute_path = True
            else:
                self.clear_path()
            self.update_target(x, y)

    def update_target(self, x, y):

        if self.targeted_entity and [x, y] != self.targeted_entity['pos']:
            self.targeted_entity = None

        if self._in_bounds(
                x, y,
                constants.MAP_VIEWPORT_X, constants.MAP_VIEWPORT_Y,
                constants.MAP_VIEWPORT_W, constants.MAP_VIEWPORT_H
        ):
            for e in self.client.closest_actors:
                if [x, y] == e['pos']:
                    self.targeted_entity = e
                    break
        elif self._in_bounds(
                x, y,
                constants.INFO_CONSOLE_X, constants.INFO_CONSOLE_Y,
                constants.INFO_CONSOLE_W, constants.INFO_CONSOLE_H
        ):
            list_entry_height = constants.ACTOR_LIST_ENTRY_HEIGHT
            actor_idx = max(0, ((y + list_entry_height - 1) //
                                list_entry_height) - 1)
            if actor_idx < len(self.client.closest_actors):
                self.targeted_entity = self.client.closest_actors[actor_idx]
                self.set_cursor_pos(*self.targeted_entity['pos'])

    def move_cursor(self, dx, dy):
        x, y = max(0, self.cursor_x + dx), max(0, self.cursor_y + dy)
        self.set_cursor_pos(x, y)

    def compute_path(self):

        if None not in (self.cursor_x, self.cursor_y):
            gs = self.client.gamestate
            map_w, map_h = gs.map['width'], gs.map['height']
            pathmap = gs.distance_map
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
        self.cursor_x, self.cursor_y = None, None
        self.targeted_entity = None
        self.path_from_cursor.clear()

    def on_entered(self):
        # We can't set a starting position in the constructor because client
        # is not set yet.
        if (self._start_x, self._start_y) != (None, None):
            self.cursor_x, self.cursor_y = self._start_x, self._start_y
        return super().on_entered()

    def update(self):
        if self.recompute_path:
            self.compute_path()
            self.recompute_path = False

        return super().update()

    def process_game_events(self, game_events):
        for ge in game_events:
            match ge:
                case {
                    'type': 'action_accepted',
                    'data': { 'type': 'move', },
                }:
                    actor = ge['data']['actor']
                    if actor['actor']['is_player'] and self.path_from_cursor:
                        self.recompute_path = True
                    elif (
                        self.targeted_entity and
                        self.targeted_entity['id'] == actor['id']
                    ):
                        actor_pos = actor['pos']
                        mw = self.client.gamestate.map['width']
                        visible_cells = self.client.gamestate.visible_cells
                        if visible_cells[c_to_idx(*actor_pos, mw)]:
                            self.targeted_entity = actor
                            self.set_cursor_pos(*actor_pos)
                        else:
                            self.clear_path()
                case {
                    'type': 'actor_died',
                    'data': {'actor': {'actor': {'is_player': False}}},
                }:
                    actor = ge['data']['actor']
                    if (
                        self.targeted_entity and
                        self.targeted_entity['id'] == actor['id']
                    ):
                        self.clear_path()

        return super().process_game_events(game_events)


class LogMessage:

    def __init__(self, msg, tick, data=None):
        self._msg = msg
        self.tick = tick
        self.data = data or {}
        self.count = 1

    @property
    def msg(self):
        msg_str = f'[{self.tick}] - {self._msg}'
        if self.count == 1:
            return msg_str
        return f'{msg_str} (x{self.count})'

    def __eq__(self, other):
        return self._msg == other._msg

    def __len__(self):
        return len(self.msg)


class GameLogMixin:

    @property
    def gamelog(self):
        return self.client.gamelog

    def log_msg(self, m, mdata=None):
        msg = LogMessage(m, self.client.gamestate.tick, mdata)
        if self.gamelog and (prev_msg := self.gamelog[-1]) == msg:
            prev_msg.count += 1
            prev_msg.tick = msg.tick
            return
        self.gamelog.append(msg)

    # FIXME: Hacky, and relies too much on knowing the internal
    # event structure (ie, we need an event type enum or mapping
    # on the client).
    def ignore_event(self, e):
        # Action failed, not initiated by the player
        if e['type'] == 'action_rejected':
            actor, target = e['data']['actor'], e['data']['target']
            if actor and 'actor' in actor and not actor['actor']['is_player']:
                return True
            if target and 'actor' in target and not target['actor']['is_player']:
                return True
        if (
            e['type'] == 'food_state_updated' and
            e['data']['state'] in ('full', 'satiated') and
            e['data']['previous_state'] in ('full',)
        ):
            return True
        return False

    def log_event(self, e):
        if self.ignore_event(e):
            return

        if e['msg']:
            self.log_msg(e['msg'], e['data'])
        # else:
        #     print(f'cant process event: {e}')

    def log_error(self, r):
        errcode, msg = r.err_code, getattr(r, 'msg', None)
        if msg:
            m = f'[REQUEST ERROR: {errcode} - {msg}]'
            self.log_msg(m, {'type': 'error'})
        else:
            print(r)

    def show_message_log(self):
        from ..modes.ui import BaseModalMode, LogModalMode
        if self.gamelog:
            self.push(LogModalMode(start_maxed=True))
        else:
            log_str = "No message logged."
            self.push(BaseModalMode(title="Messages", txt="No message logged."))


class BloodstainsMixin:

    @property
    def bloodstains(self):
        return self.client.bloodstains


class ConfirmMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.confirmed = False

    def confirm(self):
        self.confirmed = True

    def on_leaving(self):
        if self.confirmed:
            super().on_leaving()
