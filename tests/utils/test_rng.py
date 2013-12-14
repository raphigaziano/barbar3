#! /usr/bin/env python
#-*- coding:utf-8 -*-
"""Unit tests for the rng mmodule"""

import unittest

import random
from utils import rng

class TestRng(unittest.TestCase):
    """Test class for the random functions"""
    def setUp(self):
        random.seed(666)

    def tearDown(self):
        pass

    def test_randint(self):
        """Testing access to random.randint"""
        self.assertEqual(92, rng.randint(1, 200))
        self.assertEqual(71, rng.randint(25, 75))

    def test_rand_double(self):
        """Testing rng.rand_double"""
        self.assertEqual(-0.4388035102303167, rng.rand_double(-5, 5))
        self.assertEqual(4.033231539802642,   rng.rand_double(-5, 5))

    # No need to test the random module functions themselves.
    # The two previous tests asserted we do have access to them, thats enough
    # for us.

    def test_shufflecopy(self):
        """Testing that rng.shuffle_copy returns a copy of the passed list."""
        startl = ["owi", "onoes", "poupi", "roro"]
        res = rng.shuffle_copy(startl)
        self.assertNotEqual(startl, res)
        self.assertFalse(startl is res)

    def test_rolldice(self):
        """Testing rng.roll_dice"""
        self.assertEqual(9,  rng.roll_dice('2D6'))
        self.assertEqual(16, rng.roll_dice('1D20+7'))
        self.assertEqual(4,  rng.roll_dice('1D7'))
        self.assertEqual(5,  rng.roll_dice('3D4-5'))
        # TODO: check ranges ?

    def test_rolldice_exception(self):
        """Testing if rng.roll_dice raises an exception on bad input"""
        self.assertRaises(rng.DiceError, rng.roll_dice, "aDp+yui")
        self.assertRaises(rng.DiceError, rng.roll_dice, "666")
        # TODO: moar bad input

    # TODO: Finish refacto from here

    def test_checkroll(self):
        """Testing rng.check_roll"""
        for i in range(100):
            self.assertTrue(rng.check_roll("2D4+5", 9) in (True, False))
            self.assertTrue(rng.check_roll("5d9+4", 0) is True)
            self.assertTrue(rng.check_roll("1d2", 100) is False)

    def test_randomtable(self):
        """Testing rng.random_table"""
        table = {
            "owi"   : 15,
            "onoes" : 55,
            "pwal"  : 30
        }
        for i in range(100):
            self.assertTrue(rng.random_table(table) in ("owi", "onoes", "pwal"))

    def test_randomtable_exception(self):
        """Testing if rng.random_table raises an exception on bad input"""
        self.assertRaises(TypeError, rng.random_table, "somestring")
        self.assertRaises(TypeError, rng.random_table, 666)
        self.assertRaises(TypeError, rng.random_table, [])
        #moar bad input

    def test_randomizeitems(self):
        """Testing rng.randomize_items"""
        types = ["potion of health", "potion of strenght", "potion of mana"]
        descrs= [("swirly blue", "blue"),
                 ("shiny black", "black"),
                 ("deep red", "red")]

        for i in range(100):
            pot_dict = rng.randomize_items(types, descrs)

            for k, v in pot_dict.items():
                self.assertTrue(k in types)
                self.assertTrue(v in descrs)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRng))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
    input()
