#! /usr/bin/env python
#-*- coding:utf-8 -*-
""" Unit tests for the dungeon & level data structures. """
import unittest
from mock import Mock

from barbarian import dungeon
from barbarian.objects.entity import EntityContainer

class TestLevel(unittest.TestCase):

    def setUp(self):
        self.level = dungeon.Level()

    def test_level_update(self):
        """ Level.update updates all entities contained by said level. """
        self.level.actors = EntityContainer(
            [Mock() for _ in range(3)]
        )
        self.level.update(foo='foo', bar=42)
        [m.update.assert_called_once_with(self.level, foo='foo', bar=42)
         for m in self.level.actors]
