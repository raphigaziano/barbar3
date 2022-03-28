from ..modes.base import BaseGameMode, GameOverMode
from ..modes.ui import DbgMapMode, PromptDirectionMode, ItemMenuMode
from ..nw import Request
from ..event_handlers import RunEventHandler

import tcod.event


class RunMode(BaseGameMode):
    """
    Main game mode.

    This will handle actual gameplay and most direct interaction
    with the game (exploring, logging messages, etc...

    """

    event_handler_cls = RunEventHandler

    __gamelog = []
    __bloodstains = []

    def cmd_open_door(self, _):
        surrounding_doors = [
            d for d in self.get_surrounding_entities(
                self.client.gamestate.props, 'door')
            if not d['openable']['open']
        ]
        if not self._open_or_close_door(surrounding_doors):
            self.log_msg('There are no closed doors around you.')

    def cmd_close_door(self, _):
        surrounding_doors = [
            d for d in self.get_surrounding_entities(
                self.client.gamestate.props, 'door')
            if d['openable']['open']
        ]
        if not self._open_or_close_door(surrounding_doors):
            self.log_msg('There are no opened doors around you.')

    def _open_or_close_door(self, surrounding_doors):

        def use_prop(px, py):
            self.client.send_request(
                Request.action('use_prop', {'propx': px, 'propy': py}))

        def use_prop_cb(_, dx, dy):
            """
            Prompt will return a direction, use it to get the actual door
            position.

            """
            px, py = self.client.gamestate.player['pos']
            use_prop(px + dx, py + dy)

        if not surrounding_doors:
            return False

        if len(surrounding_doors) == 1:
            # Only one door around, no need to chose
            target_door = surrounding_doors[0]
            tdx, tdy = target_door['pos']
            use_prop(tdx, tdy)
        else:
            # Prompt user for direction
            self.push(PromptDirectionMode(on_leaving=use_prop_cb))

        return True

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
        self.push(AutoRunMode(action_name='move', action_data=data))

    def cmd_autoxplore(self, _):
        """ Same as above, but with an autoexploring move """
        self.push(AutoRunMode(action_name='xplore'))

    def show_inventory(self):
        def use_on_close_cb(menu):
            self.client.send_request(
                Request.action(
                    'use_item', data={'item_id': menu.selected})
            )

        self.push(
            ItemMenuMode(
                'Inventory', self.client.gamestate.inventory,
                on_leaving=use_on_close_cb)
        )

    def select_items(self, title, items, select_callback):
        self.push(ItemMenuMode(title, items, on_leaving=select_callback))

    def get_item(self):
        ppos = self.client.gamestate.player['pos']
        items = [
            item for item in self.client.gamestate.items
            if item['pos'] == ppos]
        if len(items) <= 1:
            return Request.action('get_item')
        else:
            return self.select_items(
                'Get items:', items,
                lambda menu: self._inventory_selection_callback('get_item', menu)
            )

    def drop_item(self):
        items = self.client.gamestate.inventory
        if len(items) == 0:
            self.log_msg("You don't have any item to drop")
        else:
            return self.select_items(
                'Drop items:', items,
                lambda menu: self._inventory_selection_callback('drop_item', menu)
            )

    def _inventory_selection_callback(self, action_name, menu):
        return self.client.send_request(
            Request.action(action_name, {'item_id_list': [menu.selected]})
        )

    def process_response(self, r):
        if r.status == 'OK':
            if r.gs:
                self.process_game_events(r.gs.last_events)
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
                    self.push(DbgMapMode())

                case {
                    'type': 'actor_died',
                    'data': {'actor': {'actor': {'is_player': False}}},
                }:
                    self.__bloodstains.append(ge['data']['actor']['pos'])
                case {
                    'type': 'actor_died',
                    'data': {'actor': {'actor': {'is_player': True}}},
                }:
                    self.replace_with(GameOverMode())

            self.log_event(ge)

    def log_msg(self, m):
        self.__gamelog.append((self.client.gamestate.tick, m))

    # FIXME: Hacky, and relies too much on knowing the internal
    # event structure (ie, we need an event type enum or mapping
    # on the client).
    def log_event(self, e):
        # Action failed, not initiated by the player
        if e['type'] == 'action_rejected':
            actor, target = e['data']['actor'], e['data']['target']
            if 'actor' in actor and not actor['actor']['is_player']:
                return
            if target and 'actor' in target and not target['actor']['is_player']:
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
        renderer.render_all(gamestate, self.__gamelog, self.__bloodstains)


class AutoRunMode(RunMode):
    """
    Re-run an action until interrupted, either by a game or ui event.

    """
    def __init__(self, action_name="", action_data=None):
        super().__init__()
        self.action_name = action_name
        self.action_data = action_data or {}

    def update(self):
        self.client.send_request(
            Request.action(self.action_name, self.action_data))
        request = super().update()
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
