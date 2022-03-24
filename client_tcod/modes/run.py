from ..modes.base import BaseGameMode, GameOverMode
from ..nw import Request
from ..ui_events import RunEventHandler
from .. import constants

import tcod.event


class RunMode(BaseGameMode):
    """
    Main game mode.

    This will handle actual gameplay and most direct interaction
    with the game (exploring, logging messages, etc...

    """

    ui_events = RunEventHandler()

    __gamelog = []
    __bloodstains = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mapgen_index = 0
        self.mapgen_timer = 0.0

    def cmd_open_door(self, _):
        surrounding_doors = [
            d for d in self.get_surrounding_entities(
                self.client.gamestate.props, 'door')
            if not d['openable']['open']
        ]
        return self._open_or_close_door(surrounding_doors)

    def cmd_close_door(self, _):
        surrounding_doors = [
            d for d in self.get_surrounding_entities(
                self.client.gamestate.props, 'door')
            if d['openable']['open']
        ]
        return self._open_or_close_door(surrounding_doors)

    def _open_or_close_door(self, surrounding_doors):

        if not surrounding_doors:
            print('TODO: log err msg')
        elif len(surrounding_doors) == 1:
            target_door = surrounding_doors[0]
            tdx, tdy = target_door['pos']
            self.client.send_request(
                Request.action('use_prop', {'propx': tdx, 'propy': tdy}))
        else:
            # Same as above with a warning for now
            print('FIXME: prompt user for direction!')
            target_door = surrounding_doors[0]
            tdx, tdy = target_door['pos']
            self.client.send_request(
                Request.action('use_prop', {'propx': tdx, 'propy': tdy}))

    def get_surrounding_entities(self, entity_list, entity_type=""):
        px, py = self.client.gamestate.player['pos']
        surrounding_cells = (
            # Cardinal only for now
            [px + 1, py], [px - 1, py], [px, py + 1], [px, py - 1]
        )

        def predicate(e):
            return (
                e['pos'] in surrounding_cells and
                (not entity_type or entity_type == e['type'])
            )

        return [e for e in entity_list if predicate(e)]

    def cmd_move_r(self, data):
        """ Move repeatedly until an ennemy is spotted """
        self.push(AutoRunMode, action_name='move', action_data=data)

    def cmd_autoxplore(self, _):
        """ Same as above, but with an autoexploring move """
        self.push(AutoRunMode, action_name='xplore')

    def process_response(self, r):
        if r.status == 'OK':
            self.process_game_events(self.client.gamestate.last_events)
        if r.status == 'error':
            self.log_error(r)

    def process_game_events(self, game_events):
        for ge in game_events:
            match ge:
                case {
                    'type': 'action_accepted',
                    'data': {'type': 'change_level'},
                }:
                    self.__bloodstains = []
                    self.mapgen_index = 0

                case {
                    'type': 'actor_died',
                    'data': {'actor': {'actor': {'is_player': False}}},
                }:
                    self.__bloodstains.append(ge['data']['actor']['pos'])
                case {
                    'type': 'actor_died',
                    'data': {'actor': {'actor': {'is_player': True}}},
                }:
                    self.replace_with(GameOverMode)

            self.log_event(ge)

    def log_msg(self, m):
        self.__gamelog.append((self.client.gamestate.tick, m))

    # FIXME: Hacky, and relies too much on knowing the internal
    # event structure (ie, we need an event type enum or mapping
    # on the client).
    def log_event(self, e):
        # Action failed, not initiated by the player
        if (
            e['type'] == 'action_rejected'
            and not e['data']['actor']['actor']['is_player']
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

    def render(self, gamestate, renderer):
        # Map debug mode:
        snapshots = gamestate.map_snapshots
        if constants.MAP_DEBUG and self.mapgen_index < len(snapshots):
            mapgen_step = snapshots[self.mapgen_index]
            renderer.render_map_debug(mapgen_step)
            self.mapgen_timer += 1   # FIXME incr by actual passed time
            if self.mapgen_timer >= constants.MAP_DEBUG_DELAY:
                self.mapgen_timer = 0.0
                self.mapgen_index += 1
        # Normal rendering
        else:
            renderer.render_all(gamestate, self.__gamelog, self.__bloodstains)


class AutoRunMode(RunMode):
    """
    Re-run an action until interrupted, either by a game or ui event.

    """
    def __init__(self, client, action_name="", action_data=None):
        super().__init__(client)
        self.action_name = action_name
        self.action_data = action_data or {}

    def update(self, context):
        self.client.send_request(
            Request.action(self.action_name, self.action_data))
        request = super().update(context)
        if request:
            self.pop()
            return self.client.process_request(request)

    def process_game_events(self, game_events):
        for ge in game_events:
            match ge:
                case {
                    'type': 'action_rejected',
                    'data': {
                        'actor': {'name': 'player'},
                    },
                } if ge['data']['type'] == self.action_name:
                    self.pop()
                case {'type': 'actor_spotted'}:
                    self.log_msg('Something dangerous is in view')
                    self.pop()
