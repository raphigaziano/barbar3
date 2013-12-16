#! /usr/bin/env python
#-*- coding:utf-8 -*-
""" Unit tests for the map data structure. """
import unittest

# TODO: Check actual map values
from utils.settings import MAP_W, MAP_H

import map


class TestMap(unittest.TestCase):

    def test_map_dimensions(self):
        """ Assert map is set to the set dimensions """
        # TODO: Test real shit
        self.assertEqual(MAP_W, len(map.MAP))
        self.assertEqual(MAP_H, len(map.MAP[0]))

    def test_get_cell(self):
        """ Accessing map cells """
        m = map.Map(lambda: [1] * 100)
        [self.assertEqual(
            1, m.get_cell(x, y)
        ) for y in range(10) for x in range(10)]
        m = map.Map(lambda: [0] * 100)
        [self.assertEqual(
            0, m.get_cell(x, y)
        ) for y in range(10) for x in range(10)]

    def test_invalid_map_location(self):
        """ Trying to access an out of bounds cell should raise an exception """
        m = map.Map(lambda: [1] * 10)
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
        self.fail('TODO')


