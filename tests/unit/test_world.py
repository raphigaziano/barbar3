import unittest
from unittest.mock import Mock, patch

from barbarian.world import World


class LevelMock(Mock):
    """
    Custom mock for level objects, setting tested attributes
    to dummy values.

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.start_pos = (0, 0)
        self.exit_pos = (1, 1)

        self.actors = Mock()


class TestWorld(unittest.TestCase):

    def test_current_depth_property(self):
        w = World(0, 0)
        # Incrementing current also increments max
        w.current_depth += 1
        self.assertEqual(w.current_depth, 2)
        self.assertEqual(w.max_depth, 2)
        w.current_depth += 1
        self.assertEqual(w.current_depth, 3)
        self.assertEqual(w.max_depth, 3)
        # Decrement leaves max alone
        w.current_depth -= 1
        self.assertEqual(w.current_depth, 2)
        self.assertEqual(w.max_depth, 3)

    def test_current_level(self):
        w = World(0, 0)

        w.insert_level(1)
        self.assertEqual(1, w.current_level)

        w.insert_level(2)
        w.current_depth += 1
        self.assertEqual(2, w.current_level)

    def test_insert_level(self):
        w = World(0, 0)

        w.insert_level('first')
        self.assertEqual(1, len(w.levels))
        self.assertEqual('first', w.levels[-1])

        w.insert_level('second')
        w.current_depth += 1
        self.assertEqual(2, len(w.levels))
        self.assertEqual('second', w.levels[-1])

        w.insert_level('replace second', replace_current=True)
        w.current_depth += 1
        self.assertEqual(2, len(w.levels))
        self.assertEqual('replace second', w.levels[-1])

        w.insert_level('third')
        w.current_depth += 1
        self.assertEqual(3, len(w.levels))
        self.assertEqual('third', w.levels[-1])

    @patch('barbarian.world.Level')
    def test_new_level(self, mock_level):
        w = World(0, 0)

        new_level = w.new_level()
        mock_level.assert_called_once_with(w.level_w, w.level_h, depth=1)
        new_level.build_map.assert_called_once()
        new_level.populate.assert_called_once()

    @patch('barbarian.world.Level', new_callable=LevelMock)
    def test_change_level_new_depth(self, mock_level):
        w = World(0, 0)
        w.insert_level(w.new_level())

        player = Mock()
        w.change_level(1, player)

        self.assertEqual(2, w.current_depth)
        self.assertEqual(2, len(w.levels))
        mock_level.assert_called_with(
            w.level_w, w.level_h, depth=w.current_depth)

        self.assertEqual(
            (player.pos.x, player.pos.y), w.current_level.start_pos)
        w.current_level.enter.assert_called_once_with(player)

    @patch('barbarian.world.Level', new_callable=LevelMock)
    def test_change_level_new_replace(self, mock_level):
        w = World(0, 0)
        w.insert_level(w.new_level())

        player = Mock()
        w.change_level(0, player)

        self.assertEqual(1, w.current_depth)
        self.assertEqual(1, len(w.levels))
        mock_level.assert_called_with(
            w.level_w, w.level_h, depth=w.current_depth)

        self.assertEqual(
            (player.pos.x, player.pos.y), w.current_level.start_pos)
        w.current_level.enter.assert_called_once_with(player)

    @patch('barbarian.world.Level', new_callable=LevelMock)
    def test_change_level_backtracking(self, mock_level):
        w = World(0, 0)
        w.insert_level(w.new_level())
        w.current_depth += 1
        w.insert_level(w.new_level())

        self.assertEqual(2, w.current_depth)
        self.assertEqual(2, len(w.levels))

        player = Mock()
        w.change_level(-1, player)

        self.assertEqual(1, w.current_depth)
        self.assertEqual(2, len(w.levels))
        self.assertEqual(2, mock_level.call_count)

        self.assertEqual(
            (player.pos.x, player.pos.y), w.current_level.exit_pos)
        w.current_level.enter.assert_called_once_with(player)

    def test_change_level_with_no_initial_level(self):
        w = World(0, 0)

        player = Mock()
        for delta in (-1, 0, 1):
            self.assertRaises(AssertionError, w.change_level, delta, player)
