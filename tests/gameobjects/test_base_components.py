#! /usr/bin/env python
#-*- coding:utf-8 -*-
""" Unit tests for the most basic game components """
import unittest

from mock import Mock

from barbarian.objects.entity import Entity
from barbarian.objects import components

class TestBaseComponent(unittest.TestCase):
    pass

class TestPositionComponent(unittest.TestCase):

    def setUp(self):
        e = Entity()
        self.pos = components.PositionComponent(entity=e, x=0, y=0)

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
                components.PositionComponent(entity=None, x=0, y=0)
            )
        )
        self.assertEqual(
            1, self.pos.distance_from_obj(
                components.PositionComponent(entity=None, x=1, y=0)
            )
        )
        self.assertEqual(
            1, self.pos.distance_from_obj(
                components.PositionComponent(entity=None, x=0, y=1)
            )
        )
        self.assertEqual(
            1, self.pos.distance_from_obj(
                components.PositionComponent(entity=None, x=1, y=1)
            )
        )
        self.assertEqual(
            2, self.pos.distance_from_obj(
                components.PositionComponent(entity=None, x=2, y=1)
            )
        )
        # ...

class TestMobileComponent(unittest.TestCase):

    def setUp(self):
        e = Entity()
        self.pos = components.PositionComponent(entity=e, x=0, y=0)
        e.add_component(self.pos)
        self.mobile = components.MobileComponent(entity=e)
        e.add_component(self.mobile)
        self.mock_level = Mock()
        self.mock_level.is_blocked.return_value = False
        self.mock_level.get_objects_at.return_value = [Mock(), Mock(), Mock()]

    def assertPos(self, x, y):
        """ Helper - Assert self.mobile is at the (x, y) position. """
        self.assertEqual(x, self.pos.x)
        self.assertEqual(y, self.pos.y)

    def test_simple_move(self):
        """ Basic move method """
        self.mobile.move(1, 1, self.mock_level)
        self.assertPos(1, 1)
        self.mobile.move(-1, -1, self.mock_level)
        self.assertPos(0, 0)
        self.mobile.move(0, 1, self.mock_level)
        self.assertPos(0, 1)
        self.mobile.move(10, 1, self.mock_level)
        self.assertPos(10, 2)
        # TODO: try and cover a sane set of possible inputs

    def test_blocked_move(self):
        """ Cancel move if path is blocked """
        self.mock_level.is_blocked.return_value = True

        self.mobile.move(1, 1, self.mock_level)
        self.assertPos(0, 0)
        self.mobile.move(0, 1, self.mock_level)
        self.assertPos(0, 0)
        self.mobile.move(1, 0, self.mock_level)
        self.assertPos(0, 0)
        self.mobile.move(-1, -1, self.mock_level)
        self.assertPos(0, 0)
        self.mobile.move(-1, 0, self.mock_level)
        self.assertPos(0, 0)
        self.mobile.move(0, -1, self.mock_level)
        self.assertPos(0, 0)
        self.mobile.move(1, -1, self.mock_level)
        self.assertPos(0, 0)
        self.mobile.move(-1, 1, self.mock_level)
        self.assertPos(0, 0)

    def test_move_towards(self):
        """ One step move towards a given position """
        self.mobile.move_towards(10, 10, self.mock_level)
        self.assertPos(1, 1)
        self.mobile.move_towards(10, 1, self.mock_level)
        self.assertPos(2, 1)
        self.mobile.move_towards(0, 10, self.mock_level)
        self.assertPos(1, 2)
        self.mobile.move_towards(0, 0, self.mock_level)
        self.assertPos(0, 1)
        # ...

    def test_move_towards_obj(self):
        """ One step move towards a given positioned entity """
        target = components.PositionComponent(entity=None, x=5, y=5)
        self.mobile.move_towards_obj(target, self.mock_level)
        self.assertPos(1, 1)
        self.mobile.move_towards_obj(target, self.mock_level)
        self.assertPos(2, 2)
        target.x = 0
        self.mobile.move_towards_obj(target, self.mock_level)
        self.assertPos(1, 3)
        target.y = 0
        self.mobile.move_towards_obj(target, self.mock_level)
        self.assertPos(0, 2)
        # ...

    def test_on_bump_triggered(self):
        """ `on_bump` methods should be called when entity steps on their owner's cell """
        self.mobile.move(1, 1, self.mock_level)
        for m in self.mock_level.get_objects_at(1, 1):
            m.on_bump.assert_called_once_with(self.mobile)
