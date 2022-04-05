from unittest.mock import Mock
from .base import BaseFunctionalTestCase

from barbarian.pathfinding import (
    PathBlockedError, get_path_to_target, get_step_to_target)


class TestPathfinding(BaseFunctionalTestCase):

    def test_get_path_to_target(self):

        # Open path

        level = self.build_dummy_level((
            '.....',
            '.....',
            '.....',
            '.....',
            '.....',
        ))

        path = list(get_path_to_target((0, 0), (4, 3), level))
        self.assertEqual(4, len(path))
        self.assertListEqual([(1, 1), (2, 2), (3, 3), (4, 3)], path)

        # Simple block

        level = self.build_dummy_level((
            '.....',
            '.....',
            '..#..',
            '.....',
            '.....',
        ))

        path = list(get_path_to_target((0, 0), (4, 3), level))
        self.assertEqual(4, len(path))
        self.assertListEqual([(1, 1), (2, 1), (3, 2), (4, 3)], path)

        # Corridor

        level = self.build_dummy_level((
            '######',
            '#....#',
            '..##.#',
            '####.#',
            '######',
        ))

        path = list(get_path_to_target((0, 2), (4, 3), level))
        self.assertEqual(5, len(path))
        self.assertListEqual([(1, 1), (2, 1), (3, 1), (4, 2), (4, 3)], path)

    def test_path_blocked_by_prop(self):

        level = self.build_dummy_level((
            '.....',
            '.....',
            '.....',
            '.....',
            '.....',
        ))
        door = self.spawn_prop(2, 2, 'door')
        door.physics.blocks = True
        level.props.add_e(door)

        path = list(get_path_to_target((0, 0), (4, 3), level))
        self.assertEqual(4, len(path))
        self.assertListEqual([(1, 1), (2, 1), (3, 2), (4, 3)], path)

        door.physics.blocks = False

        path = list(get_path_to_target((0, 0), (4, 3), level))
        self.assertEqual(4, len(path))
        self.assertListEqual([(1, 1), (2, 2), (3, 3), (4, 3)], path)

    def test_path_blocked_by_actor(self):

        level = self.build_dummy_level((
            '.....',
            '.....',
            '.....',
            '.....',
            '.....',
        ))
        rat = self.spawn_actor(2, 2, 'rat')
        rat.physics.blocks = True
        level.actors.add_e(rat)

        path = list(get_path_to_target((0, 0), (4, 3), level))
        self.assertEqual(4, len(path))
        self.assertListEqual([(1, 1), (2, 1), (3, 2), (4, 3)], path)

        rat.physics.blocks = False

        path = list(get_path_to_target((0, 0), (4, 3), level))
        self.assertEqual(4, len(path))
        self.assertListEqual([(1, 1), (2, 2), (3, 3), (4, 3)], path)

    def test_path_not_blocked_by_items(self):

        level = self.build_dummy_level((
            '.....',
            '.....',
            '.....',
            '.....',
            '.....',
        ))
        pot = self.spawn_item(2, 2, 'health_potion')
        pot.physics = Mock(blocks=True)
        level.items.add_e(pot)

        path = list(get_path_to_target((0, 0), (4, 3), level))
        self.assertEqual(4, len(path))
        # Same path as below: items are not checked, so the blocks
        # attribute doesn't change anything.
        self.assertListEqual([(1, 1), (2, 2), (3, 3), (4, 3)], path)

        pot.physics.blocks = False

        path = list(get_path_to_target((0, 0), (4, 3), level))
        self.assertEqual(4, len(path))
        self.assertListEqual([(1, 1), (2, 2), (3, 3), (4, 3)], path)

    def test_get_step(self):

        level = self.build_dummy_level((
            '.#.',
            '...',
        ))
        dx, dy = get_step_to_target((0, 0), (2, 0), level)
        self.assertEqual((1, 1), (dx, dy))

    def test_path_blocked(self):

        level = self.build_dummy_level((
            '#######',
            '#.....#',
            '#..@..#',
            '#######',
            '#...o.#',
            '#.....#',
            '#######',
        ))

        orc = level.actors[3,2]
        player = level.actors[4,4]

        path = get_path_to_target(
            (orc.pos.x, orc.pos.y),
            (player.pos.x, player.pos.y), level)
        # Need to consume generator
        self.assertRaises(PathBlockedError, next, path)
