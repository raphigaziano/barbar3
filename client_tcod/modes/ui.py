from ..modes.base import BaseGameMode, GameOverMode
from ..ui_events import DbgMapEventHandler, PromptDirectionEventHandler
from .. import constants


class DbgMapMode(BaseGameMode):
    """ No-op mode used for debug rendering. """

    ui_events = DbgMapEventHandler()

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


class PromptDirectionMode(BaseGameMode):

    ui_events = PromptDirectionEventHandler()

    prompt = 'Chose a direction (esc to cancel): '

    def update(self, context):

        res = super().update(context)
        if isinstance(res, tuple):
            dx, dy = res
            self.on_leaving(dx, dy)
            self.pop()
        else:
            return res

    def render(self, gamestate, renderer):
        renderer.render_prompt(self.prompt)
