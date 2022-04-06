from unittest.mock import MagicMock, patch
import random

from tests.functional.base import BaseFunctionalTestCase

from barbarian.utils.rng import Rng
from barbarian.genmap import _MAP_BUILDERS
from barbarian.world import Level
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

    MAP_W, MAP_H = 30, 30
    seed = None     # Use this to debug potential test fails

    def test_spawn_is_deterministic(self):

        Rng.init_root(self.seed)
        Rng.add_rng('dungeon')
        Rng.add_rng('sapwn')

        print('Rng seed:', Rng.root.initial_seed)

        # Save rng state
        rng_state = Rng.spawn.getstate()

        # Generate a few level and store them for reuse (we don't want
        # to generate new maps for the second spawn run).

        levels = []

        for BuilderCls in _MAP_BUILDERS:

            level = Level(self.MAP_W, self.MAP_H)
            with patch(
                'barbarian.world.get_map_builder',
                return_value=BuilderCls(debug=False)
            ):
                level.build_map(False)
                levels.append(level)

        # Spawn entities for each leavel and store the results

        no_perturb_entities = []

        for level in levels:
            level.populate()    # calls spawn_level
            for e_list in (
                level.props.all, level.items.all, level.actors.all
            ):
                # Sort entities (no matter as long as we can reproduce it):
                # items are stored in an unordered set, so we can't guarantee
                # comparison will de done in the right order.
                for e in sorted(e_list, key=lambda e: e._id):
                    no_perturb_entities.append(e)

        # Copy levels, leaving entities alone

        new_levels = []

        for level in levels:
            new_level = Level(self.MAP_W, self.MAP_H)
            new_level.map = level.map
            new_level.start_pos = level.start_pos
            new_level.exit_pos = level.exit_pos
            new_level.spawn_zones = level.spawn_zones

            new_levels.append(new_level)

        # Reset rng state
        Rng.spawn.setstate(rng_state)

        # Rerun the build and spawn code, spamming the other rngs along
        # the way

        perturb_entities = []

        for i, level in enumerate(new_levels):

            # Random mess \o/
            Rng.randint(0, random.randint(2, 10))
            Rng.dungeon.roll_dice_str(f'{i}D{i*2}+3')
            random.randrange(Rng.roll_dice_str(f'2d{i+1}'))
            Rng.dungeon.choice([random.random() for _ in range(i+1)])

            level.populate()    # calls spawn_level
            for e_list in (
                level.props.all, level.items.all, level.actors.all
            ):
                # Sort entities (no matter as long as we can reproduce it):
                # items are stored in an unordered set, so we can't guarantee
                # comparison will de done in the right order.
                for e in sorted(e_list, key=lambda e: e._id):
                    perturb_entities.append(e)

        # Compare results...

        self.assertEqual(len(no_perturb_entities), len(perturb_entities))

        for unperturbed, perturbed in zip(no_perturb_entities, perturb_entities):
            # Force a dummy EntityId to avoid messing up the comparison
            unperturbed._id = 1
            perturbed._id = 1
            self.assertDictEqual(unperturbed.serialize(), perturbed.serialize())
