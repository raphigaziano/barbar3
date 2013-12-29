#! /usr/bin/env python
#-*- coding:utf-8 -*-
""" Unit tests for the most basic game components """
import unittest

from barbarian.objects import components

class TestBaseComponent(unittest.TestCase):
    pass

class TestPositionComponent(unittest.TestCase):

    def setUp(self):
        self.pos = components.MobileComponent(x=0, y=0)

    def test_distance(self):
        """ Base distance helper """
        self.assertEqual(0, self.pos.distance_from(0, 0))
        self.assertEqual(1, self.pos.distance_from(1, 0))
        self.assertEqual(1, self.pos.distance_from(0, 1))
        self.assertEqual(1, self.pos.distance_from(1, 1))
        self.assertEqual(2, self.pos.distance_from(2, 0))
        self.assertEqual(2, self.pos.distance_from(0, 2))
        self.assertEqual(2, self.pos.distance_from(1, 2))
        self.assertEqual(3, self.pos.distance_from(2, 3))
        # ...

    def test_distance_obj(self):
        """ Distance from object """
        self.assertEqual(
            0, self.pos.distance_from_obj(
                components.PositionComponent(x=0, y=0)
            )
        )
        self.assertEqual(
            1, self.pos.distance_from_obj(
                components.PositionComponent(x=1, y=0)
            )
        )
        self.assertEqual(
            1, self.pos.distance_from_obj(
                components.PositionComponent(x=0, y=1)
            )
        )
        self.assertEqual(
            1, self.pos.distance_from_obj(
                components.PositionComponent(x=1, y=1)
            )
        )
        self.assertEqual(
            2, self.pos.distance_from_obj(
                components.PositionComponent(x=2, y=1)
            )
        )
        # ...

