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

    def __init__(self, title, items, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.menu_items = items
        self.cursor_idx = 0
        self._selected = None

    @property
    def selected(self):
        if self._selected:
            return self._selected[0]
        return None

    def set_cursor(self, cursor_dir):
        _, dy = cursor_dir
        if dy == 0:
            return
        self.cursor_idx += dy
        if self.cursor_idx < 0:
            self.cursor_idx = len(self.menu_items) - 1
        elif self.cursor_idx == len(self.menu_items):
            self.cursor_idx = 0

    def select_item(self):
        self._selected = self.menu_items[self.cursor_idx]

    def on_leaving(self):
        if self.selected:
            super().on_leaving()

    def render(self, gamestate, renderer):
        renderer.render_menu(self)


class ItemMenuMode(MenuMode):

    def __init__(self, title, items, *args, **kwargs):
        items = [(item['id'], item['name']) for item in items]
        super().__init__(title, items, *args, **kwargs)
