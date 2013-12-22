#! /usr/bin/env python
#-*- coding:utf-8 -*-
""" Unit tests for the map data structure. """
import unittest

from barbarian import gamestates

class TestStateManager(unittest.TestCase):

    def setUp(self):
        self.sm = gamestates.StateManager()

    def test_initial_state(self):
        """ Instanciating a StateManager with an initial state """
        state = object()
        sm = gamestates.StateManager(state)
        self.assertEqual(1, len(sm._states))
        self.assertTrue(sm.current_state is state)


    def test_current_state(self):
        """ StateManager.current_state points to the top of the stack """
        dummy_state = object()
        self.sm.push(dummy_state)
        self.assertTrue(dummy_state is self.sm.current_state)

        another_state = object()
        self.sm.push(another_state)
        self.assertTrue(another_state is self.sm.current_state)

        self.sm.pop()
        self.assertTrue(dummy_state is self.sm.current_state)

    def test_invalid_current_state(self):
        """ StateManager.current_state raise an Exception if no states in the stack """
        # NOTE: this is the current behaviour, not necesserally the desired
        # one.
        self.assertRaises(IndexError, getattr, self.sm, 'current_state')

    def test_is_done(self):
        """ StateManager.is_done should return True of no states are on the stack, False otherwise """
        self.assertTrue(self.sm.is_done)
        self.sm.push(object())
        self.assertFalse(self.sm.is_done)
        self.sm.pop()
        self.assertTrue(self.sm.is_done)

    def test_push(self):
        """ Stack like methods - Pushing """
        s1, s2, s3 = object(), object(), object()
        self.assertEqual(0, len(self.sm._states))

        self.sm.push(s1)
        self.assertEqual(1, len(self.sm._states))
        self.assertTrue(self.sm._states[0] is s1)
        self.sm.push(s2)
        self.assertEqual(2, len(self.sm._states))
        self.assertTrue(self.sm._states[0] is s1)
        self.assertTrue(self.sm._states[1] is s2)
        self.sm.push(s3)
        self.assertEqual(3, len(self.sm._states))
        self.assertTrue(self.sm._states[0] is s1)
        self.assertTrue(self.sm._states[1] is s2)
        self.assertTrue(self.sm._states[2] is s3)

    def test_pop(self):
        """ Stack like methods - Poping """
        s1, s2, s3 = object(), object(), object()
        self.sm.push(s1)
        self.sm.push(s2)
        self.sm.push(s3)

        self.assertEqual(3, len(self.sm._states))
        self.assertTrue(self.sm.current_state is s3)

        self.sm.pop()
        self.assertEqual(2, len(self.sm._states))
        self.assertTrue(self.sm.current_state is s2)

        self.sm.pop()
        self.assertEqual(1, len(self.sm._states))
        self.assertTrue(self.sm.current_state is s1)

        self.sm.pop()
        self.assertEqual(0, len(self.sm._states))

    # Updating tests:
    # - mock contained states to assert their update and render methods are
    # called?

    def test_push_next_state_on_update(self):
        """ Pushing next scheduled state on the stack """
        s = gamestates.GameState()
        new_state = gamestates.GameState()
        s.next_state = new_state
        self.sm.push(s)
        self.sm.update()

        self.assertEqual(2, len(self.sm._states))
        self.assertTrue(new_state is self.sm.current_state)

    def test_pop_state_on_update(self):
        """ Popping current state off the stack if requested """
        old_state = gamestates.GameState()
        cur_state = gamestates.GameState()
        cur_state.done = True
        self.sm.push(old_state)
        self.sm.push(cur_state)
        self.sm.update()

        self.assertEqual(1, len(self.sm._states))
        self.assertTrue(old_state is self.sm.current_state)

    def test_replace_on_update(self):
        """ Pop & Push ie State replacement """
        s = gamestates.GameState()
        new_state = gamestates.GameState()
        s.done = True
        s.next_state = new_state
        self.sm.push(s)
        self.sm.update()

        self.assertEqual(1, len(self.sm._states))
        self.assertTrue(new_state is self.sm.current_state)

class TestBaseState(unittest.TestCase):

    def setUp(self):
        self.sm = gamestates.StateManager()
        self.state = gamestates.GameState()
        self.sm.push(self.state)

    def test_pop(self):
        """ Pop trigger """
        self.state._pop()
        self.assertTrue(self.state.done)
        self.sm.update()
        self.assertEqual(0, len(self.sm._states))

    def test_push(self):
        """ Push trigger """
        next_state = gamestates.GameState()
        self.state._push(next_state)
        self.assertTrue(next_state is self.state.next_state)
        self.sm.update()
        self.assertEqual(2, len(self.sm._states))
        self.assertTrue(self.sm._states[0] is self.state)
        self.assertTrue(self.sm._states[1] is next_state)

    def test_replace(self):
        """ State replacement trigger """
        next_state = gamestates.GameState()
        self.state._replace_with(next_state)
        self.assertTrue(next_state is self.state.next_state)
        self.sm.update()
        self.assertEqual(1, len(self.sm._states))
        self.assertTrue(self.sm._states[0] is next_state)

