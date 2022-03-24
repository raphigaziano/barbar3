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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.gamelog = []
        self.bloodstains = []
        self.mapgen_index = 0
        self.mapgen_timer = 0.0

    def cmd_change_level(self, data):
        """
        Regen the current level, or restart the game if it's not
        running.

        """
        self.client.send_request(Request.action('change_level'))
        status = self.client.response.status
        if (
            status == 'error' and
            self.client.response.err_code == 'NOT_RUNNING'
        ):
            self.client.send_request(Request.start())

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

    # TODO: have a dedicated "auto" mode for this ?
    def _repeat_cmd(self, action_name, data=None):
        """ 
        Re-run an action until interrupted, either by an game or
        ui event.

        """
        data = data or {}
        while True:
            self.client.send_request(Request.action(action_name, data))
            self.client.render()
            request = self.ui_events.handle(self.client.context)
            if request:
                return self.client.process_request(request)
            for ge in self.client.gamestate.last_events:
                match ge:
                    case {
                        'type': 'action_rejected',
                        'data': {
                            # FIXME: this should be one or the other,
                            # depending on the action.
                            # Can case check a passed in dict ???
                            'type': ('move' | 'xplore'),
                            'actor': {'name': 'player'},
                        },
                    }:
                        break
                    case {'type': 'actor_spotted'}:
                        self.log_msg('Something dangerous is in view')
                        break
            else:
                continue
            break

    def cmd_move_r(self, data):
        """ Move repeatedly until an ennemy is spotted """
        self._repeat_cmd('move', data)

    def cmd_autoxplore(self, _):
        """ Same as above, but with an autoexploring move """
        self._repeat_cmd('xplore')

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
                    self.bloodstains = []
                    self.mapgen_index = 0

                case {
                    'type': 'actor_died',
                    'data': {'actor': {'actor': {'is_player': False}}},
                }:
                    self.bloodstains.append(ge['data']['actor']['pos'])
                case {
                    'type': 'actor_died',
                    'data': {'actor': {'actor': {'is_player': True}}},
                }:
                    self.replace_with(GameOverMode)

            self.log_event(ge)

    def log_msg(self, m):
        self.gamelog.append((self.client.gamestate.tick, m))

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
            renderer.render_all(
                gamestate, self.gamelog, self.bloodstains)
