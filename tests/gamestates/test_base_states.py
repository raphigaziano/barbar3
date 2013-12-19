#! /usr/bin/env python
#-*- coding:utf-8 -*-
""" Unit tests for the map data structure. """
import unittest

import gamestates

class TestStateManager(unittest.TestCase):

    def setUp(self):
        self.cs = gamestates.StateManager()

    def test_initial_state(self):
        """ Instanciating a StateManager with an initial state """
        state = object()
        cs = gamestates.StateManager(state)
        self.assertEqual(1, len(cs._states))
        self.assertTrue(cs.current_state is state)


    def test_current_state(self):
        """ StateManager.current_state points to the top of the stack """
        dummy_state = object()
        self.cs.push(dummy_state)
        self.assertTrue(dummy_state is self.cs.current_state)

        another_state = object()
        self.cs.push(another_state)
        self.assertTrue(another_state is self.cs.current_state)

        self.cs.pop()
        self.assertTrue(dummy_state is self.cs.current_state)

    def test_invalid_current_state(self):
        """ StateManager.current_state raise an Exception if no states in the stack """
        # NOTE: this is the current behaviour, not necesserally the desired
        # one.
        self.assertRaises(IndexError, getattr, self.cs, 'current_state')

    def test_is_done(self):
        """ StateManager.is_done should return True of no states are on the stack, False otherwise """
        self.assertTrue(self.cs.is_done)
        self.cs.push(object())
        self.assertFalse(self.cs.is_done)
        self.cs.pop()
        self.assertTrue(self.cs.is_done)

    def test_push(self):
        """ Stack like methods - Pushing """
        s1, s2, s3 = object(), object(), object()
        self.cs.push(s1)
        self.assertEqual(1, len(self.cs._states))
        self.assertTrue(self.cs._states[0] is s1)
        self.cs.push(s2)
        self.assertEqual(2, len(self.cs._states))
        self.assertTrue(self.cs._states[1] is s2)
        self.cs.push(s3)
        self.assertEqual(3, len(self.cs._states))
        self.assertTrue(self.cs._states[2] is s3)

    def test_pop(self):
        """ Stack like methods - Poping """
        s1, s2, s3 = object(), object(), object()
        self.cs.push(s1)
        self.cs.push(s2)
        self.cs.push(s3)

        self.assertEqual(3, len(self.cs._states))
        self.assertTrue(self.cs._states[-1] is s3)

        self.cs.pop()
        self.assertEqual(2, len(self.cs._states))
        self.assertTrue(self.cs._states[-1] is s2)

        self.cs.pop()
        self.assertEqual(1, len(self.cs._states))
        self.assertTrue(self.cs._states[-1] is s1)

        self.cs.pop()
        self.assertEqual(0, len(self.cs._states))

        self.assertRaises(IndexError, self.cs.pop)

    # Updating tests:
    # - mock contained test to assert their update and render methods are
    # called?
    # - simulate request for pushing or poping... This is the big one.
    #   Some of that will be handled by GameStateTest.

# BaseGamseState Tests
# ...
