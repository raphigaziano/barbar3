import os

from ..modes.base import BaseGameMode, GameOverMode
from ..event_handlers import (
    DbgMapEventHandler,
    PagedModalEventHandler,
    PromptConfirmEventHandler,
    PromptDirectionEventHandler,
    MenuEventHandler,
    TargetingEventHandler,
)
from ..utils import c_to_idx, closest_open_cell, path_to
from .. import constants


class DbgMapMode(BaseGameMode):
    """ No-op mode used for debug rendering. """

    event_handler_cls = DbgMapEventHandler

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mapgen_index = 0
        self.mapgen_timer = 0.0
        self.running = True

    def set_map_index(self, delta):
        self.mapgen_index = min(
            max(0, self.mapgen_index + delta),
            len(self.client.gamestate.map_snapshots) - 1
        )

    def process_response(self, response):
        for ge in response.gs.last_events:
            # reset index if we spam regen level
            match ge:
                case {
                    'type': 'action_accepted',
                    'data': {'type': 'change_level'},
                }:
                    self.mapgen_index = 0

    def update(self):

        snapshots = self.client.gamestate.map_snapshots

        if (
            constants.MAP_DEBUG and
            self.running and
            self.mapgen_index < len(snapshots)
        ):
            self.mapgen_timer += 1
            # FIXME incr by actual passed time 
            if self.mapgen_timer >= constants.MAP_DEBUG_DELAY:
                self.mapgen_timer = 0.0
                self.mapgen_index += 1

        if self.mapgen_index == len(snapshots):
            self.pop()

        return super().update()

    def render(self, gamestate, renderer):
        snapshots = gamestate.map_snapshots
        try:
            mapgen_step = snapshots[self.mapgen_index]
            renderer.render_map_debug(mapgen_step)
        except IndexError:
            pass


class CursorMixin:

    def __init__(self, cx=None, cy=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cursor_x, self.cursor_y = cx, cy
        self.recompute_path = False
        self.path_from_cursor = []

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
        if self.recompute_path:
            self.compute_path()
            self.recompute_path = False

        return super().update()

    def update_gamestate(self, gs):
        super().update_gamestate(gs)
        gs.cursor_pos = (self.cursor_x, self.cursor_y)
        gs.path_from_cursor = self.path_from_cursor


class TargetMode(CursorMixin, BaseGameMode):

    event_handler_cls = TargetingEventHandler

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.confirmed = False

    def confirm(self):
        self.confirmed = True

    def on_leaving(self):
        if self.confirmed:
            super().on_leaving()

    def render(self, gamestate, renderer):
        # FIXME: This cause rendering bugs (log and bloodstains disapear).
        # Waiting for a cleanup commit to handle this.
        renderer.render_all(gamestate, [], [])


class BaseModalMode(BaseGameMode):

    event_handler_cls = PagedModalEventHandler
    title = ""
    txt = ""

    def __init__(self, title="", txt='', start_maxed=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title or self.title
        self.txt = txt or self.txt
        self.offset = self.max_offset if start_maxed else 0

    @property
    def max_offset(self):
        nlines = len(self.txt.splitlines())
        return nlines - constants.MAX_MODAL_HEIGHT

    def set_offset(self, delta):
        self.offset = max(0, self.offset + delta)
        if self.offset > self.max_offset:
            self.offset = self.max_offset

    def render(self, gamestate, renderer):
        renderer.render_modal(self.title, self.txt, self.offset)


class HelpModalMode(BaseModalMode):

    title = "Help"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open(os.path.join(constants.ASSETS_PATH, 'help_screen.txt')) as f:
            self.txt = f.read()


class PromptConfirmMode(BaseModalMode):

    event_handler_cls = PromptConfirmEventHandler

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.txt = f'{self.txt} [Yn]'
        self.confirmed = False

    def confirm(self):
        self.confirmed = True

    def on_leaving(self):
        if self.confirmed:
            super().on_leaving()


class PromptDirectionMode(BaseModalMode):

    event_handler_cls = PromptDirectionEventHandler
    txt = 'Chose a direction (esc to cancel): '


class MenuMode(BaseGameMode):

    event_handler_cls = MenuEventHandler

    def __init__(self, title, options, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.menu_options = options
        self.cursor_idx = 0
        self._selected = None

    @property
    def selected(self):
        if self._selected:
            return self._selected[0]
        return None

    def select_option(self, idx=None):
        select_idx = idx or self.cursor_idx
        try:
            self._selected = self.menu_options[select_idx]
            self.pop()
        except IndexError:
            pass

    def set_cursor(self, cursor_dir):
        _, dy = cursor_dir
        if dy == 0:
            return
        self.cursor_idx += dy
        if self.cursor_idx < 0:
            self.cursor_idx = len(self.menu_options) - 1
        elif self.cursor_idx == len(self.menu_options):
            self.cursor_idx = 0

    def on_leaving(self):
        if self.selected:
            super().on_leaving()

    def render(self, gamestate, renderer):
        renderer.render_menu(self)


class ItemMenuMode(MenuMode):

    STACKED_ITEM_TYPES = ('potion', 'scroll', 'food')

    def __init__(self, title, items, *args, **kwargs):
        items = self.stack_items(items)
        super().__init__(title, items, *args, **kwargs)

    def stack_items(self, flat_item_list):

        # This works for now, but is already pretty hacky and risk
        # becoming a beast.
        # While I like handling stacking on the client side, moving
        # the bookkeeping to the server is probably easier and more
        # maintainable, unless we figure out a better way to keep it
        # here.
        # Will need to think about it, and too lazy to handle this 
        # right now.

        stacks_counter = {}
        for i, item in enumerate(flat_item_list):
            if item['type'] in self.STACKED_ITEM_TYPES:
                if 'consumable' in item:
                    charges, max_charges = (
                        item['consumable']['charges'],
                        item['consumable']['max_charges'])
                else:
                    charges, max_charges = 0, 0
            else:
                # Non stackable item: use flat idx to ensure 'key' is
                # different from any other
                charges, max_charges = i, i

            item_key = (item['name'], charges, max_charges)
            item_count = stacks_counter.get(item_key, (0, None))[0]
            stacks_counter[item_key] = (item_count + 1, item)

        item_list = []
        for item_key, item_val in stacks_counter.items():
            item_name, charges, max_charges = item_key
            count, item = item_val
            display_str = self.get_display_string(count, item)
            item_list.append((item['id'], display_str))

        # Sort by (name, count) ?

        return item_list

    def get_display_string(self, count, item):

        item_name = item['name']

        display_str = (
            f'({count}) {item_name}' if count > 1 else item_name)

        # TODO: We'll probably want to list *some* but not
        # all, 1 charges items (ie, wands)
        if (consumable := item.get('consumable', None)):
            charges, max_charges = (
                consumable['charges'], consumable['max_charges'])
            if charges != max_charges or charges > 1:
                display_str += f' (remaining charges: {charges}'

        return display_str


class InventoryMenuMode(ItemMenuMode):

    def __init__(self, title, inventory, *args, **kwargs):
        self.inventory = inventory
        super().__init__(title, self.inventory['items'], *args, **kwargs)

    def get_display_string(self, count, item):

        display_string = super().get_display_string(count, item)

        if ((equipable := item.get('equipable', None)) and
            (slot_item := self.inventory['slots'][equipable['inventory_slot']]) and
            item['id'] == slot_item['id']
        ):
            display_string += ' (Equiped)'

        return display_string
