#! /usr/bin/env python
""" Unit tests for the geometric utilities. """
import unittest

from barbarian.utils.geometry import Rect

class TestRect(unittest.TestCase):

    def test_center(self):
        """ Getting the center position of a given rect """
        r = Rect(0, 0, 10, 10)
        self.assertEqual((5, 5), r.center)
        r = Rect(0, 0, 5, 10)
        self.assertEqual((2, 5), r.center)
        r = Rect(0, 0, 10, 5)
        self.assertEqual((5, 2), r.center)
        r = Rect(0, 0, 1, 1)
        self.assertEqual((0, 0), r.center)

    def test_intersects(self):
        """ Rect intersections """
        r1, r2 = Rect(0, 0, 10, 10), Rect(5, 5, 10, 10)
        self.assertTrue(r1.intersect(r2))
        self.assertTrue(r2.intersect(r1))
        r1, r2 = Rect(0, 0, 10, 10), Rect(10, 10, 10, 10)
        self.assertTrue(r1.intersect(r2))
        self.assertTrue(r2.intersect(r1))
        r1, r2 = Rect(0, 0, 10, 10), Rect(11, 11, 10, 10)
        self.assertFalse(r1.intersect(r2))
        self.assertFalse(r2.intersect(r1))
        r1, r2 = Rect(30, 20, 10, 10), Rect(11, 11, 10, 10)
        self.assertFalse(r1.intersect(r2))
        self.assertFalse(r2.intersect(r1))
        # ...


