#! /usr/bin/env python
#-*- coding:utf-8 -*-
""" Unit tests for the map data structure. """
import unittest

from barbarian import map

class TestMap(unittest.TestCase):

    def test_get_cell(self):
        """ Accessing map cells """
        m = map.Map(10, 10, [1] * 100)
        [self.assertEqual(1, m.get_cell(x, y))
         for y in range(10) for x in range(10)]
        m = map.Map(10, 10, [0] * 100)
        [self.assertEqual(0, m.get_cell(x, y))
         for y in range(10) for x in range(10)]

    def test_indexing(self):
        """ Direct indexing shortcut """
        m = map.Map(10, 10, [1] * 100)
        [self.assertEqual(1, m[x, y]) for y in range(10) for x in range(10)]
        # Passing an explicit tuple should also work
        [self.assertEqual(1, m[(x, y)]) for y in range(10) for x in range(10)]

        m = map.Map(10, 10, [0] * 100)
        [self.assertEqual(0, m[x, y]) for y in range(10) for x in range(10)]
        # Passing an explicit tuple should also work
        [self.assertEqual(0, m[(x, y)]) for y in range(10) for x in range(10)]

    def test_indexing_errors(self):
        """ Indexing overload accepts only specific args """
        # 2 args required
        m = map.Map(5, 5, [1] * 50)
        self.assertRaises(IndexError, m.__getitem__, (0,))
        self.assertRaises(IndexError, m.__getitem__, (0, 0, 0))

        # No slicing
        self.assertRaises(TypeError, m.__getitem__, slice(1, 1))
        self.assertRaises(TypeError, m.__getitem__, slice(1, 1, 1))

    def test_invalid_map_location(self):
        """ Trying to access an out of bounds cell should raise an exception """
        m = map.Map(2, 8, [1] * 10)
        self.assertRaises(
            map.OutOfBoundMapError, m.get_cell, *(10, 10)
        )
        self.assertRaises(
            map.OutOfBoundMapError, m.get_cell, *(0, 10)
        )
        self.assertRaises(
            map.OutOfBoundMapError, m.get_cell, *(10, 0)
        )

    def test_iter(self):
        """ Iterating directly over Map objects """
        m = map.Map(3, 3, range(9))
        dummy_map = [
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
        ]
        for x, y, c in m:
            self.assertEqual(dummy_map[x][y], m.get_cell(x, y))

    def test_helper_cart_to_idx(self):
        """ Converting cartesian coodrinates to array index """
        m = map.Map(10, 10, [1] * 100)
        self.assertEqual(0,  m._cartesian_to_idx(0, 0))
        self.assertEqual(1,  m._cartesian_to_idx(1, 0))
        self.assertEqual(9,  m._cartesian_to_idx(9, 0))
        self.assertEqual(10, m._cartesian_to_idx(0, 1))
        self.assertEqual(54, m._cartesian_to_idx(4, 5))
        self.assertEqual(55, m._cartesian_to_idx(5, 5))
        self.assertEqual(56, m._cartesian_to_idx(6, 5))
        self.assertEqual(45, m._cartesian_to_idx(5, 4))
        self.assertEqual(65, m._cartesian_to_idx(5, 6))
        self.assertEqual(90, m._cartesian_to_idx(0, 9))
        self.assertEqual(99, m._cartesian_to_idx(9, 9))


    def test_helper_idx_to_cart(self):
        """ Converting array index to cartesian coordinates """
        m = map.Map(10, 10, [1] * 100)
        self.assertEqual((0, 0), m._idx_to_cartesian(0))
        self.assertEqual((1, 0), m._idx_to_cartesian(1))
        self.assertEqual((9, 0), m._idx_to_cartesian(9))
        self.assertEqual((0, 1), m._idx_to_cartesian(10))
        self.assertEqual((4, 5), m._idx_to_cartesian(54))
        self.assertEqual((5, 5), m._idx_to_cartesian(55))
        self.assertEqual((0, 9), m._idx_to_cartesian(90))
        self.assertEqual((9, 9), m._idx_to_cartesian(99))

    def test_helpers_round_trip(self):
        """ From indexes to cartesian and back & vice versa """
        m = map.Map(10, 10, [1] * 100)
        [self.assertEqual(
            i, m._cartesian_to_idx(*m._idx_to_cartesian(i))
        ) for i in range(100)]
        [self.assertEqual(
            (x, y), m._idx_to_cartesian(m._cartesian_to_idx(x, y))
        ) for x, y, _ in m]

    def test_slice(self):
        """ Getting a new map from a portion of an existing one """
        cells = [
            'a', 'b', 'c', 'd', 'e',
            'f', 'g', 'h', 'i', 'j',
            'k', 'l', 'm', 'n', 'o',
            'p', 'q', 'r', 's', 't',
            'u', 'v', 'w', 'x', 'y'
        ]
        m = map.Map(5, 5, cells)

        new_m = m.slice(1, 2, 2, 2)
        self.assertListEqual(['l', 'm', 'q', 'r'], new_m.cells)
        # FIXME: test More edge cases

    def test_slice_from_rect(self):
        """ Getting a map slice from a given Rect object """
        from barbarian.utils.geometry import Rect
        cells = [
            'a', 'b', 'c', 'd', 'e',
            'f', 'g', 'h', 'i', 'j',
            'k', 'l', 'm', 'n', 'o',
            'p', 'q', 'r', 's', 't',
            'u', 'v', 'w', 'x', 'y'
        ]
        m = map.Map(5, 5, cells)
        r = Rect(1, 2, 2, 2)

        new_m = m.slice_from_rect(r)
        self.assertListEqual(['l', 'm', 'q', 'r'], new_m.cells)
