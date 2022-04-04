from ..modes.base import BaseGameMode, GameOverMode
from ..event_handlers import (
    DbgMapEventHandler,
    PromptConfirmEventHandler,
    PromptDirectionEventHandler,
    MenuEventHandler,
)
from .. import constants


class DbgMapMode(BaseGameMode):
    """ No-op mode used for debug rendering. """

    event_handler_cls = DbgMapEventHandler

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mapgen_index = 0
        self.mapgen_timer = 0.0

    def process_response(self, response):
        for ge in self.client.gamestate.last_events:
            # reset index if we spam regen level
            match ge:
                case {
                    'type': 'action_accepted',
                    'data': {'type': 'change_level'},
                }:
                    self.mapgen_index = 0

    def render(self, gamestate, renderer):
        snapshots = gamestate.map_snapshots
        if constants.MAP_DEBUG and self.mapgen_index < len(snapshots):
            mapgen_step = snapshots[self.mapgen_index]
            renderer.render_map_debug(mapgen_step)
            self.mapgen_timer += 1
            # FIXME incr by actual passed time 
            if self.mapgen_timer >= constants.MAP_DEBUG_DELAY:
                self.mapgen_timer = 0.0
                self.mapgen_index += 1
        else:
            self.pop()


class BasePromptMode(BaseGameMode):

    prompt = ''

    def __init__(self, prompt='', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompt = prompt or self.prompt

    def render(self, gamestate, renderer):
        renderer.render_prompt(self.prompt)


class PromptConfirmMode(BasePromptMode):

    event_handler_cls = PromptConfirmEventHandler

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompt = f'{self.prompt} [Yn]'
        self.confirmed = False

    def confirm(self):
        self.confirmed = True

    def on_leaving(self):
        if self.confirmed:
            super().on_leaving()


class PromptDirectionMode(BasePromptMode):

    event_handler_cls = PromptDirectionEventHandler
    prompt = 'Chose a direction (esc to cancel): '


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

    def __init__(self, title, items, *args, **kwargs):
        items = self.stack_items(items)
        super().__init__(title, items, *args, **kwargs)

    def stack_items(self, flat_item_list):

        counter = {}
        for item in flat_item_list:
            if 'consumable' in item:
                charges, max_charges = (
                    item['consumable']['charges'],
                    item['consumable']['max_charges'])
            else:
                charges, max_charges = 0, 0
            item_key = (item['name'], charges, max_charges)
            item_count = counter.get(item_key, (0, None))[0]
            counter[item_key] = (item_count +1, item)

        item_list = []
        for item_key, item_val in counter.items():
            item_name, charges, max_charges = item_key
            count, item = item_val
            display_str = self.get_display_string(
                count, item, charges, max_charges)
            item_list.append((item['id'], display_str))

        # Sort by (name, count) ?

        return item_list

    def get_display_string(self, count, item, charges, max_charges):

        item_name = item['name']

        display_str = (
            f'({count}) {item_name}' if count > 1 else item_name)

        # TODO: We'll probably want to list *some* but not
        # all, 1 charges items (ie, wands)
        if charges != max_charges or charges > 1:
            display_str += f' (remaining charges: {charges}'

        return display_str


class InventoryMenuMode(ItemMenuMode):

    def __init__(self, title, inventory, *args, **kwargs):
        self.inventory = inventory
        super().__init__(title, self.inventory['items'], *args, **kwargs)

    def get_display_string(self, count, item, charges, max_charges):
        display_string = super().get_display_string(count, item, charges, max_charges)

        if ((equipable := item.get('equipable', None)) and
            (slot_item := self.inventory['slots'][equipable['inventory_slot']]) and
            item['id'] == slot_item['id']
        ):
            display_string += ' (Equiped)'

        return display_string
