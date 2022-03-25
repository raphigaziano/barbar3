from ..modes.base import BaseGameMode, GameOverMode
from ..event_handlers import (
    DbgMapEventHandler,
    PromptConfirmEventHandler,
    PromptDirectionEventHandler)
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
            self.callback('_cb_on_leaving')


class PromptDirectionMode(BasePromptMode):

    event_handler_cls = PromptDirectionEventHandler
    prompt = 'Chose a direction (esc to cancel): '
