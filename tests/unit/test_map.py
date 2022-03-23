import unittest

from barbarian.map import Map, TileType


class TestBaseMapBuilder(unittest.TestCase):

    def test_in_bound_ignore_border(self):
        m = Map(5, 5)

        self.assertTrue(m.in_bounds(0, 0))
        self.assertFalse(m.in_bounds(0, 0, border_width=1))
        self.assertTrue(m.in_bounds(1, 1, border_width=1))
        self.assertFalse(m.in_bounds(1, 1, border_width=2))

        self.assertTrue(m.in_bounds(4, 4))
        self.assertFalse(m.in_bounds(4, 4, border_width=1))
        self.assertTrue(m.in_bounds(3, 3, border_width=1))
        self.assertFalse(m.in_bounds(3, 3, border_width=2))

    def test_cell_blocks(self):
        m = Map(3, 3)
        for tt in TileType:
            m[1,1] = tt
            if tt == TileType.WALL:
                self.assertTrue(m.cell_blocks(1, 1))
            else:
                self.assertFalse(m.cell_blocks(1, 1))

    def test_serialize(self):
        m = Map(3, 3, [TileType.WALL] * 9)

        expected = {
            'width': 3,
            'height': 3,
            'cells': ['#', '#', '#', '#', '#', '#', '#', '#', '#'],
            'bitmask_grid': None,
        }
        self.assertEqual(m.serialize(), expected)

        m = Map(3, 3, [TileType.FLOOR] * 9)
        m.compute_bitmask_grid()

        expected = {
            'width': 3,
            'height': 3,
            'cells': ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
            'bitmask_grid': [5, 1, 9, 4, 0, 8, 6, 2, 10],
        }
        self.assertEqual(m.serialize(), expected)
