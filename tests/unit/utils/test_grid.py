import unittest
from unittest.mock import Mock

from barbarian.utils.geometry import Rect
from barbarian.utils.structures.grid import (
    Grid, EntityGrid, GridContainer, GridError, OutOfBoundGridError)


class TestGrid(unittest.TestCase):

    def test_invalid_cell_list_length(self):
        self.assertRaises(GridError, Grid, 3, 3, [0] * 12)

    def test_get_cell(self):
        """ Accessing map cells """
        g = Grid(10, 10, [1] * 100)
        [self.assertEqual(1, g.get_cell(x, y))
         for y in range(10) for x in range(10)]
        g = Grid(10, 10, [0] * 100)
        [self.assertEqual(0, g.get_cell(x, y))
         for y in range(10) for x in range(10)]

    def test_in_bounds(self):
        g = Grid(3, 3)
        for x in range(g.w):
            for y in range(g.h):
                self.assertTrue(g.in_bounds(x, y))

        for invalid_pos in (
            (-1, 0), (1, -1), (3, 0), (0, 3), (3, 3),
        ):
            self.assertFalse(g.in_bounds(*invalid_pos))

    def test_indexing(self):
        """ Direct indexing shortcut """
        g = Grid(10, 10, [1] * 100)
        [self.assertEqual(1, g[x, y]) for y in range(10) for x in range(10)]
        # Passing an explicit tuple should also work
        [self.assertEqual(1, g[(x, y)]) for y in range(10) for x in range(10)]

        g = Grid(10, 10, [0] * 100)
        [self.assertEqual(0, g[x, y]) for y in range(10) for x in range(10)]
        # Passing an explicit tuple should also work
        [self.assertEqual(0, g[(x, y)]) for y in range(10) for x in range(10)]

    def test_indexing_errors(self):
        """ Indexing overload accepts only specific args """
        # 2 args required
        g = Grid(5, 5, [1] * 25)
        self.assertRaises(IndexError, g.__getitem__, (0,))
        self.assertRaises(IndexError, g.__getitem__, (0, 0, 0))

        # No slicing
        self.assertRaises(TypeError, g.__getitem__, slice(1, 1))
        self.assertRaises(TypeError, g.__getitem__, slice(1, 1, 1))

    def test_invalid_grid_location(self):
        """ Trying to access an out of bounds cell should raise an exception """
        g = Grid(2, 8, [1] * 16)
        self.assertRaises(
            OutOfBoundGridError, g.get_cell, 10, 10
        )
        self.assertRaises(
            OutOfBoundGridError, g.get_cell, 0, 10
        )
        self.assertRaises(
            OutOfBoundGridError, g.get_cell, 10, 0
        )
        self.assertRaises(
            OutOfBoundGridError, g.get_cell, -1, -1
        )

    def test_iter(self):
        """ Iterating directly over Grid objects """
        g = Grid(3, 3, range(9))
        dummy_map = [
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
        ]
        for x, y, c in g:
            self.assertEqual(dummy_map[x][y], g.get_cell(x, y))

    def test_helper_cart_to_idx(self):
        """ Converting cartesian coodrinates to array index """
        g = Grid(10, 10, [1] * 100)
        self.assertEqual(0,  g._cartesian_to_idx(0, 0))
        self.assertEqual(1,  g._cartesian_to_idx(1, 0))
        self.assertEqual(9,  g._cartesian_to_idx(9, 0))
        self.assertEqual(10, g._cartesian_to_idx(0, 1))
        self.assertEqual(54, g._cartesian_to_idx(4, 5))
        self.assertEqual(55, g._cartesian_to_idx(5, 5))
        self.assertEqual(56, g._cartesian_to_idx(6, 5))
        self.assertEqual(45, g._cartesian_to_idx(5, 4))
        self.assertEqual(65, g._cartesian_to_idx(5, 6))
        self.assertEqual(90, g._cartesian_to_idx(0, 9))
        self.assertEqual(99, g._cartesian_to_idx(9, 9))

    def test_helper_idx_to_cart(self):
        """ Converting array index to cartesian coordinates """
        g = Grid(10, 10, [1] * 100)
        self.assertEqual((0, 0), g._idx_to_cartesian(0))
        self.assertEqual((1, 0), g._idx_to_cartesian(1))
        self.assertEqual((9, 0), g._idx_to_cartesian(9))
        self.assertEqual((0, 1), g._idx_to_cartesian(10))
        self.assertEqual((4, 5), g._idx_to_cartesian(54))
        self.assertEqual((5, 5), g._idx_to_cartesian(55))
        self.assertEqual((0, 9), g._idx_to_cartesian(90))
        self.assertEqual((9, 9), g._idx_to_cartesian(99))

    def test_helpers_round_trip(self):
        """ From indexes to cartesian and back & vice versa """
        g = Grid(10, 10, [1] * 100)
        [self.assertEqual(
            i, g._cartesian_to_idx(*g._idx_to_cartesian(i))
        ) for i in range(100)]
        [self.assertEqual(
            (x, y), g._idx_to_cartesian(g._cartesian_to_idx(x, y))
        ) for x, y, _ in g]

    def test_get_neighbors(self):
        g = Grid(3, 3, [0] * 9)
        g[1,1] = 1

        neighbors = list(g.get_neighbors(1, 1))
        self.assertEqual(len(neighbors), 8)

        expected_coords = [
            (1, 0), (2, 1), (1, 2), (0, 1),     # cardinals
            (2, 0), (2, 2), (0, 2), (0, 0),     # diagonals
        ]
        self.assertListEqual(
            [(x, y) for x, y, _ in neighbors],
            expected_coords)
        self.assertListEqual(
            [c for _, __, c in neighbors],
            [0] * 8)

    def test_get_neighbors_cardinal_only(self):
        g = Grid(3, 3, [0] * 9)
        g[1,1] = 1

        neighbors = list(g.get_neighbors(1, 1, cardinal_only=True))
        self.assertEqual(len(neighbors), 4)

        expected_coords = [
            (1, 0), (2, 1), (1, 2), (0, 1),     # cardinals
        ]
        self.assertListEqual(
            [(x, y) for x, y, _ in neighbors],
            expected_coords)
        self.assertListEqual(
            [c for _, __, c in neighbors],
            [0] * 4)

    def test_neighbors_gets_out_of_bounds(self):
        g = Grid(3, 3, [0] * 9)
        # Get neighbors from the N-E corner
        neighbors = list(g.get_neighbors(2, 0))
        self.assertEqual(len(neighbors), 3)

        expected_coords = [
            (2, 1), (1, 0),     # cardinals: South, West
            (1, 1),             # diagonals: SouthWest
        ]
        self.assertListEqual(
            [(x, y) for x, y, _ in neighbors],
            expected_coords)

    def test_get_neighbors_predicate(self):
        g = Grid(3, 3, [0] * 9)

        neighbors = list(g.get_neighbors(
            1, 1, predicate=lambda _, __, c: c == 1))
        self.assertEqual(len(neighbors), 0)

        g[0,0] = 1
        g[0,1] = 1
        g[2,2] = 1

        neighbors = list(g.get_neighbors(
            1, 1, predicate=lambda _, __, c: c == 1))
        self.assertEqual(len(neighbors), 3)
        cells = [c for _, __, c in neighbors]
        self.assertTrue(all(c == 1 for c in cells))
        pos = [(x, y) for x, y, _ in neighbors]
        self.assertIn((0, 0), pos)
        self.assertIn((0, 1), pos)
        self.assertIn((2, 2), pos)

        neighbors = list(g.get_neighbors(
            1, 1, predicate=lambda x, y, _: x != 0))
        self.assertEqual(len(neighbors), 5)
        self.assertTrue(all(x != 0 for x, _, __ in neighbors))

    def test_slice(self):
        """ Getting a new map from a portion of an existing one """
        cells = [
            'a', 'b', 'c', 'd', 'e',
            'f', 'g', 'h', 'i', 'j',
            'k', 'l', 'm', 'n', 'o',
            'p', 'q', 'r', 's', 't',
            'u', 'v', 'w', 'x', 'y'
        ]
        g = Grid(5, 5, cells)

        new_m = g.slice(1, 2, 2, 2)
        self.assertListEqual(['l', 'm', 'q', 'r'], new_m.cells)
        # FIXME: test More edge cases

    def test_slice_from_rect(self):
        """ Getting a map slice from a given Rect object """
        cells = [
            'a', 'b', 'c', 'd', 'e',
            'f', 'g', 'h', 'i', 'j',
            'k', 'l', 'm', 'n', 'o',
            'p', 'q', 'r', 's', 't',
            'u', 'v', 'w', 'x', 'y'
        ]
        g = Grid(5, 5, cells)
        r = Rect(1, 2, 2, 2)

        new_m = g.slice_from_rect(r)
        self.assertListEqual(['l', 'm', 'q', 'r'], new_m.cells)


class TestEntityGrid(unittest.TestCase):

    def test_add_objects(self):
        eg = EntityGrid(2, 2)
        eg.add(0, 0, 'obj1')
        eg.add(0, 0, 'obj2')
        eg.add(0, 1, 'obj3')
        # obj2 has replaced obj1
        self.assertEqual(eg[0,0], 'obj2')
        self.assertEqual(eg[0,1], 'obj3')

    def test_remove_objects(self):
        eg = EntityGrid(2, 2)
        eg.add(0, 0, 'obj')
        self.assertEqual(eg[0,0], 'obj')
        eg.remove(0, 0, 'dummy_value_will_be_ignored')
        self.assertEqual(eg[0,0], None)

    def test_len(self):
        eg = EntityGrid(2, 2)
        eg.add(0, 0, 'obj1')
        eg.add(0, 1, 'obj2')
        eg.add(1, 1, 'obj3')
        self.assertEqual(len(eg), 3)

    def test_all(self):
        eg = EntityGrid(2, 2)
        eg.add(0, 0, 'obj1')
        eg.add(0, 1, 'obj2')
        eg.add(1, 1, 'obj3')
        self.assertEqual(
            sorted(eg.all), sorted(['obj1', 'obj2', 'obj3']))

    def test_iter(self):
        eg = EntityGrid(3, 3)
        eg.add(0, 0, 'a')
        eg.add(0, 1, 'b')
        eg.add(1, 1, 'c')
        eg.add(2, 2, 'd')

        dummy_map = [
            ('a',   'b',    None),
            (None,  'c',    None),
            (None,  None,   'd'),
        ]
        for x, y, o in eg:
            self.assertEqual(o, dummy_map[x][y])

    def test_add_entity(self):
        e = Mock(pos=Mock(x=1, y=0))
        eg = EntityGrid(2, 2)
        eg.add_e(e)
        self.assertEqual(e, eg[1,0])

    def test_remove_entity(self):
        e = Mock(pos=Mock(x=1, y=0))
        eg = EntityGrid(2, 2)
        eg[1,0] = e

        eg.remove_e(e)
        self.assertIsNone(eg[1,0])


class TestGridContainer(unittest.TestCase):

    def test_add_objects(self):
        gc = GridContainer(2, 2)
        gc.add(0, 0, 'obj1')
        gc.add(0, 0, 'obj2')
        gc.add(0, 1, 'obj3')
        self.assertEqual(gc[0,0], {'obj1', 'obj2'})
        self.assertEqual(gc[0,1], {'obj3'})

    def test_remove_objects(self):
        gc = GridContainer(2, 2)
        gc.add(0, 0, 'obj1')
        gc.add(0, 0, 'obj2')
        self.assertEqual(gc[0,0], {'obj1', 'obj2'})
        gc.remove(0, 0, 'obj1')
        self.assertEqual(gc[0,0], {'obj2'})

    def test_len(self):
        gc = GridContainer(2, 2)
        gc.add(0, 0, 'obj1')
        gc.add(0, 0, 'obj2')
        gc.add(0, 1, 'obj3')
        self.assertEqual(len(gc), 3)

    def test_all(self):
        gc = GridContainer(2, 2)
        gc.add(0, 0, 'obj1')
        gc.add(0, 0, 'obj2')
        gc.add(0, 1, 'obj3')
        self.assertEqual(sorted(gc.all), sorted(['obj1', 'obj2', 'obj3']))

    def test_iter(self):
        gc = GridContainer(3, 3)
        gc.add(0, 0, 'obj1')
        gc.add(0, 0, 'obj2')
        gc.add(0, 1, 'obj3')
        gc.add(1, 1, 'obj4')
        gc.add(2, 2, 'obj5')

        dummy_map = [
            (['obj1', 'obj2'], ['obj3'], []),
            ([], ['obj4'], []),
            ([], [], ['obj5']),
        ]
        for x, y, o in gc:
            self.assertIn(o, dummy_map[x][y])

    def test_add_entity(self):
        e = Mock(pos=Mock(x=1, y=0))
        gc = GridContainer(2, 2)
        gc.add_e(e)
        self.assertIn(e, gc[1,0])

    def test_remove_entity(self):
        e = Mock(pos=Mock(x=1, y=0))
        gc = GridContainer(2, 2)
        gc[1,0].add(e)
        self.assertEqual(len(gc[1,0]), 1)

        gc.remove_e(e)
        self.assertEqual(len(gc[1,0]), 0)
