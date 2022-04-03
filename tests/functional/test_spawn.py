from unittest.mock import MagicMock, patch

from tests.functional.base import BaseFunctionalTestCase

from barbarian.utils.rng import Rng
from barbarian.spawn import (
    spawn_entity, spawn_zone, spawn_door, spawn_level)
from barbarian.settings import MAX_SPAWNS


class TestSpawnZone(BaseFunctionalTestCase):

    def setUp(self):
        super().setUp()
        Rng.add_rng('spawn')

    def test_spawn_zone(self):

        level = self.build_dummy_level(('...', '...', '...'))
        zone = tuple((x, y) for x, y, _ in level.map)

        # Bypass actual table roll
        roll_results = [
            {'name': 'health_potion'},
            {'name': 'trap'},
            {'name': 'kobold'},
            {'name': 'scroll_blink'},
        ]

        with patch(
                'barbarian.utils.rng._Rng.roll_table',
                side_effect=roll_results
        ) as patched_roller:

            spawn_zone(level, zone, [], n_spawns=MAX_SPAWNS)

            self.assertEqual(MAX_SPAWNS, patched_roller.call_count)

            self.assertEqual(1, len(level.actors))
            self.assertEqual('kobold', level.actors.all[0].typed.type)

            self.assertEqual(1, len(level.props))
            self.assertEqual('trap', level.props.all[0].typed.type)

            self.assertEqual(2, len(level.items))
            self.assertIn('potion', (i.typed.type for _, __, i in level.items))
            self.assertIn('scroll', (i.typed.type for _, __, i in level.items))

    def test_invalid_entity_name(self):
        with patch(
            'barbarian.utils.rng._Rng.roll_table', return_value={'name': 'WOOT'}
        ):
            with self.assertLogs('barbarian.spawn', 'WARNING'):
                # Need to ensure we'll spawn at least one entity, otherwise
                # nothing will be logged
                spawn_zone(None, [], [], n_spawns=1)

    def test_no_spawn_on_occupied_cell(self):

        zone = ((0, 0),)
        spawn_table = [(5, {'name': 'orc'})]

        level = self.build_dummy_level()
        level.props.add_e(self.spawn_prop(0, 0, 'door'))
        spawn_zone(level, zone, spawn_table, n_spawns=MAX_SPAWNS)
        # Spawn cancelled
        self.assertEqual(0, len(level.actors))

        level = self.build_dummy_level()
        level.actors.add_e(self.spawn_actor(0, 0, 'rat'))
        spawn_zone(level, zone, spawn_table, n_spawns=MAX_SPAWNS)
        # Spawn cancelled, but blocking actor is still on the level
        self.assertEqual(1, len(level.actors))

        level = self.build_dummy_level()
        level.items.add_e(self.spawn_item(0, 0, 'health_potion'))
        spawn_zone(level, zone, spawn_table, n_spawns=MAX_SPAWNS)
        # Spawn ok: items don't block
        self.assertEqual(1, len(level.actors))

    def test_n_spawns(self):

        level = self.build_dummy_level(('...', '...', '...'))
        zone = tuple((x, y) for x, y, _ in level.map)
        spawn_table = [(5, {'name': 'orc', 'n': 3})]

        spawn_zone(level, zone, spawn_table, n_spawns=1)
        self.assertEqual(3, len(level.actors))

    @patch('barbarian.utils.rng._Rng.roll_dice', return_value=4)
    def test_n_spawns_dice_str(self, _):

        level = self.build_dummy_level(('...', '...', '...'))
        zone = tuple((x, y) for x, y, _ in level.map)
        spawn_table = [(5, {'name': 'orc', 'n': '1d8'})]

        spawn_zone(level, zone, spawn_table, n_spawns=1)
        self.assertEqual(4, len(level.actors))

    def test_spawn_pack(self):

        level = self.build_dummy_level(('...', '...', '...'))
        zone = tuple((x, y) for x, y, _ in level.map)
        spawn_table = [
            (5, {'name': 'rat_and_kobold_pack', 'n': 3, 'subtable': [
                    {"name": 'rat', 'weight': 5},
                    {"name": 'kobold', 'weight': 5},
                ]
            })
        ]

        spawn_zone(level, zone, spawn_table, n_spawns=1)
        self.assertEqual(3, len(level.actors))
        for actor in level.actors.all:
            self.assertIn(actor.typed.type, ('rat', 'kobold'))

# No tests for spawn_stairs. Funtion is very simple and mimics
# so many other helpers, so no real point in explicetely testing it.

@patch('barbarian.spawn.spawn_entity', wraps=spawn_entity)
class TestSpawnDoor(BaseFunctionalTestCase):

    dummy_map = (
        '###.###',
        '###.###',    # Door spot at 3, 1
        '##...##',
        '##.....',    # Door spot at 5, 3
        '.....##',    # Door spot at 1, 4
        '#####.#',    # Corner (invalid) at 5, 5
    )

    def test_spawn_door(self, spawner):
        level = self.build_dummy_level()
        valid_spawn_points = [(3, 1), (5, 3), (1, 4)]
        # Technically invalid points, but spawn_door will trat them as valid.
        # Doesn't seem to cause trouble as long as we only call it on
        # room borders, but we may want to fix it anyway.
        valid_no_wall = [(2, 2), (4, 2), (4, 4)]

        for x, y, _ in level.map:
            spawner.reset_mock()

            spawn_door(level, x, y)
            if (x, y) in valid_spawn_points:
                spawner.assert_called_once()
            elif (x, y) in valid_no_wall:
                spawner.assert_called_once()
            else:
                spawner.assert_not_called()

    def test_spawn_door_out_of_bounds(self, spawner):
        level = self.build_dummy_level()
        spawn_door(level, -1, -1)
        spawn_door(level, 50, 78)
        spawner.assert_not_called()

    def test_spawn_door_on_wall_cell(self, spawner):
        # Already validated above, but let's be explicit
        level = self.build_dummy_level()
        for x, y, _ in level.map:
            if self.dummy_map[y][x] == '#':
                spawn_door(level, x, y)

        spawner.assert_not_called()

    def test_spawn_door_on_open_cell(self, spawner):
        # Already validated above, but let's be explicit
        level = self.build_dummy_level()
        spawn_door(level, 3, 3)     # room center
        spawner.assert_not_called()

    def test_door_on_cell_blocked_by_prop(self, spawner):
        level = self.build_dummy_level()
        prop = MagicMock()
        prop.physics.blocks = True
        # Place blocking prop at valid cell 3, 1
        level.props.add(3, 1, prop)

        spawn_door(level, 3, 1)
        spawner.assert_not_called()


class TestSpawnLevel(BaseFunctionalTestCase):

    @patch('barbarian.spawn.spawn_zone')
    @patch('barbarian.spawn.spawn_door')
    @patch('barbarian.spawn.spawn_stairs')
    def test_spawn_level(self, stairs_spawner, door_spawner, zone_spawner):

        class RoomMock(MagicMock):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.x = self.y = 2
                self.x2 = self.y2 = 4

        level = self.build_dummy_level()
        level.start_pos = 1, 2
        level.exit_pos = 3, 4
        level.map.rooms = [RoomMock(), RoomMock(), RoomMock()]

        spawn_zones = [((1, 2),), ((3, 4),), ((5, 6),)]
        spawn_level(level, spawn_zones)

        stairs_spawner.assert_any_call(level, 1, 2, 'stairs_up')
        stairs_spawner.assert_any_call(level, 3, 4, 'stairs_down')

        # Wall length (4) * num_walls (4) * num_rooms (3) = 48
        self.assertEqual(48, door_spawner.call_count)

        self.assertEqual(len(level.map.rooms), zone_spawner.call_count)
