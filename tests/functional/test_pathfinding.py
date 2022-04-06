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
        expected_path = [(1, 0), (2, 1), (3, 2), (4, 3)]
        self.assertEqual(len(expected_path), len(path))
        self.assertListEqual(expected_path, path)

        # Simple block

        level = self.build_dummy_level((
            '.....',
            '.....',
            '...#.',
            '.....',
            '.....',
        ))

        path = list(get_path_to_target((0, 0), (4, 3), level))
        expected_path = [(1, 1), (2, 2), (3, 3), (4, 3)]
        self.assertEqual(len(expected_path), len(path))
        self.assertListEqual(expected_path, path)

        # Corridor

        level = self.build_dummy_level((
            '######',
            '#....#',
            '..##.#',
            '####.#',
            '######',
        ))

        path = list(get_path_to_target((0, 2), (4, 3), level))
        expected_path = [(1, 2), (2, 1), (3, 1), (4, 2), (4, 3)]
        self.assertEqual(len(expected_path), len(path))
        self.assertListEqual(expected_path, path)

    def test_path_blocked_by_prop(self):

        level = self.build_dummy_level((
            '.....',
            '.....',
            '...+.',
            '.....',
            '.....',
        ))
        door = level.props[3, 2]
        door.physics.blocks = True
        level.props.add_e(door)

        path = list(get_path_to_target((0, 0), (4, 3), level))
        expected_path = [(1, 1), (2, 2), (3, 3), (4, 3)]
        self.assertEqual(len(expected_path), len(path))
        self.assertListEqual(expected_path, path)

        door.physics.blocks = False

        path = list(get_path_to_target((0, 0), (4, 3), level))
        expected_path = [(1, 0), (2, 1), (3, 2), (4, 3)]
        self.assertEqual(len(expected_path), len(path))
        self.assertListEqual(expected_path, path)

    def test_path_blocked_by_actor(self):

        level = self.build_dummy_level((
            '.....',
            '.....',
            '...o.',
            '.....',
            '.....',
        ))
        orc = level.actors[3, 2]
        orc.physics.blocks = True
        level.actors.add_e(orc)

        path = list(get_path_to_target((0, 0), (4, 3), level))
        expected_path = [(1, 1), (2, 2), (3, 3), (4, 3)]
        self.assertEqual(len(expected_path), len(path))
        self.assertListEqual(expected_path, path)

        orc.physics.blocks = False

        path = list(get_path_to_target((0, 0), (4, 3), level))
        expected_path = [(1, 0), (2, 1), (3, 2), (4, 3)]
        self.assertEqual(len(expected_path), len(path))
        self.assertListEqual(expected_path, path)

    def test_path_not_blocked_by_items(self):

        level = self.build_dummy_level((
            '.....',
            '.....',
            '...!.',
            '.....',
            '.....',
        ))
        pot = list(level.items[3, 2])[0]
        pot.physics = Mock(blocks=True)
        level.items.add_e(pot)

        path = list(get_path_to_target((0, 0), (4, 3), level))
        expected_path = [(1, 0), (2, 1), (3, 2), (4, 3)]
        self.assertEqual(len(expected_path), len(path))
        self.assertListEqual(expected_path, path)

        pot.physics.blocks = False

        # Same path as above: items are not checked, so the blocks
        # attribute doesn't change anything.
        path = list(get_path_to_target((0, 0), (4, 3), level))
        expected_path = [(1, 0), (2, 1), (3, 2), (4, 3)]
        self.assertEqual(len(expected_path), len(path))
        self.assertListEqual(expected_path, path)

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
