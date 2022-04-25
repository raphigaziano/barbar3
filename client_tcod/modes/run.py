from ..modes.base import BaseGameMode, GameOverMode
from ..modes.mixins import CursorMixin, GameLogMixin, BloodstainsMixin
from ..modes.ui import (
    DbgMapMode, PromptDirectionMode, ItemMenuMode, InventoryMenuMode,
)
from ..nw import Request
from ..event_handlers import (
    RunEventHandler, MoveToEventHandler, TargetingEventHandler)
from ..constants import AUTO_REST_N_TURNS

import tcod.event


class RunMode(CursorMixin, GameLogMixin, BloodstainsMixin, BaseGameMode):
    """
    Main game mode.

    This will handle actual gameplay and most direct interaction
    with the game (exploring, logging messages, etc...

    """
    event_handler_cls = RunEventHandler

    def open_door(self):
        surrounding_doors = [
            d for d in self.get_surrounding_entities(
                self.client.gamestate.props, 'door')
            if not d['openable']['open']
        ]
        if not self._open_or_close_door(surrounding_doors):
            self.log_msg('There are no closed doors around you.')

    def close_door(self):
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

    def rest_r(self, n_turns=AUTO_REST_N_TURNS):
        """ Rest for n turn """
        self.push(AutoRunMode(action_name='idle', n_turns=n_turns))

    def move_r(self, data):
        """ Move repeatedly until an ennemy is spotted """
        self.push(AutoRunMode(action_name='move', action_data=data))

    def autoxplore(self):
        """ Same as above, but with an autoexploring move """
        self.push(AutoRunMode(action_name='xplore'))

    def show_inventory(self):
        def use_on_close_cb(menu):
            self.client.send_request(
                Request.action('use_item', data={'item_id': menu.selected}))

        self.push(
            InventoryMenuMode(
                'Inventory', self.client.gamestate.inventory,
                on_leaving=use_on_close_cb)
        )

    def get_item(self):
        ppos = self.client.gamestate.player['pos']
        items = [
            item for item in self.client.gamestate.items
            if item['pos'] == ppos]
        if len(items) <= 1:
            return Request.action('get_item')
        else:
            return self.push(ItemMenuMode(
                'Get items:', items,
                on_leaving=lambda menu:
                    self._item_selection_callback('get_item', menu))
            )

    def drop_item(self):
        inventory = self.client.gamestate.inventory
        if len(inventory['items']) == 0:
            self.log_msg("You don't have any item to drop")
        else:
            return self.push(InventoryMenuMode(
                'Drop items:', inventory,
                on_leaving=lambda menu:
                    self._item_selection_callback('drop_item', menu))
            )

    def wield_item(self):

        def _item_filter(item):
            return (
                'equipable' in item and
                item['equipable']['inventory_slot'] == 'weapon')

        inventory = self.client.gamestate.inventory.copy()
        inventory['items'] = filter(_item_filter, inventory['items'])
        return self.push(InventoryMenuMode(
            'Wield items:', inventory,
            on_leaving=lambda menu:
                self._item_selection_callback('equip_item', menu))
        )

    wearable_slots = ('shield', 'armor', 'helmet', 'boots', 'gloves',)

    def wear_item(self):

        def _item_filter(item):
            return (
                'equipable' in item and
                item['equipable']['inventory_slot'] in self.wearable_slots)

        inventory = self.client.gamestate.inventory.copy()
        inventory['items'] = filter(_item_filter, inventory['items'])
        return self.push(InventoryMenuMode(
            'Wear items:', inventory,
            on_leaving=lambda menu:
                self._item_selection_callback('equip_item', menu))
        )

    def eat(self):

        def _item_filter(item):
            return 'edible' in item

        inventory = self.client.gamestate.inventory.copy()
        inventory['items'] = filter(_item_filter, inventory['items'])
        return self.push(InventoryMenuMode(
            'Eat item:', inventory,
            on_leaving=lambda menu:
                self.client.send_request(
                    Request.action('use_item', data={'item_id': menu.selected}))
        ))

    def _item_selection_callback(self, action_name, menu):
        return self.client.send_request(
            Request.action(action_name, {'item_id_list': [menu.selected]})
        )

    def process_response(self, r):
        super().process_response(r)
        if r.status == 'error':
            self.log_error(r)

    def process_game_events(self, game_events):

        super().process_game_events(game_events)

        for ge in game_events:
            match ge:
                case {
                    'type': 'action_accepted',
                    'data': {'type': 'change_level'},
                }:
                    self.bloodstains.clear()
                    self.push(DbgMapMode())
                case {
                    'type': 'action_accepted',
                    'data': {'type': 'inflict_dmg'},
                }:
                    target = ge['data']['target']
                    self.client.renderer.emit_particle(
                        *target['pos'], glyph='*', fg=(255, 0, 0)
                    )
                    if (target['actor']['is_player'] and
                        target['health']['wounded']
                    ):
                        badly_wounded = target['health']['badly_wounded']
                        warn_level = 2 if badly_wounded else 1
                        self.log_msg(
                            f"Low hp: " +
                            f"{target['health']['hp']}/{target['health']['max_hp']}",
                            mdata={'type': 'ui_warning', 'warn_level': warn_level}
                        )
                        if badly_wounded:
                            self.client.renderer.flash_color(255, 0, 0)
                case {
                    'type': 'actor_died',
                    'data': {'actor': {'actor': {'is_player': False}}},
                }:
                    self.bloodstains.append(ge['data']['actor']['pos'])
                case {
                    'type': 'actor_died',
                    'data': {'actor': {'actor': {'is_player': True}}},
                }:
                    self.replace_with(GameOverMode())

            self.log_event(ge)

    def render(self, gamestate, renderer):
        renderer.render_all(gamestate)


class AutoRunMode(RunMode):
    """
    Re-run an action until interrupted, either by a game or ui event.

    """
    def __init__(self, action_name="", action_data=None, n_turns=None, **kwargs):
        super().__init__(**kwargs)
        self.action_name = action_name
        self.action_data = action_data or {}
        self.n_turns = n_turns

    def update(self):

        if self.n_turns:
            self.n_turns -= 1
            if self.n_turns <= 0:
                self.pop()

        self.send_action_request()
        request = super().update()
        if request:
            self.pop()

    def send_action_request(self):
        self.client.send_request(
            Request.action(self.action_name, self.action_data))

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
                case {
                    'type': 'action_accepted',
                    'data': {
                        'type': 'inflict_dmg',
                        'target': {'name': 'player'},
                    },
                }:
                    self.pop()
                case {
                    'type': 'actor_spotted',
                    'data': {
                        'spotter': {'name': 'player'},
                    },
                }:
                    self.log_msg(
                        'Something dangerous is in view',
                        mdata={'type': 'ui_warning', 'warn_level': 1})
                    self.pop()

        super().process_game_events(game_events)


class MoveToMode(AutoRunMode):

    event_handler_cls = MoveToEventHandler

    def __init__(self, path, *args, **kwargs):
        self.path = path.copy()
        if path:
            kwargs['cx'], kwargs['cy'] = path[0]
        super().__init__('move', *args, **kwargs)
        self.recompute_path = True

    def send_action_request(self):
        if self.path:
            ppx, ppy = self.client.gamestate.player['pos']
            dx, dy = self.path.pop()
            self.action_data = {'dir': (dx - ppx, dy - ppy)}
            return super().send_action_request()
        else:
            self.pop()
