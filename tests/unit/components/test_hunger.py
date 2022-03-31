import unittest
from unittest.mock import patch

from barbarian.components.actor import HungerClock


class TestHungerComponent(unittest.TestCase):

    MAX_SATIATION = 12
    HUNGER_STATES = (
        ('starving', 2),
        ('very hungry', 4),
        ('hungry', 8),
        ('satiated', 12),
    )

    def setUp(self):
        max_satiation_patcher = patch(
            'barbarian.components.actor.MAX_HUNGER_SATIATION', self.MAX_SATIATION)
        max_satiation_patcher.start()
        hunger_states_patcher = patch(
            'barbarian.components.actor.HUNGER_STATES', self.HUNGER_STATES)
        hunger_states_patcher.start()

        self.addCleanup(max_satiation_patcher.stop)
        self.addCleanup(hunger_states_patcher.stop)

    def test_full(self):

        clock = HungerClock(rate=1, satiation=12)

        for val in (12,):
            clock.satiation = val
            self.assertTrue(clock.full, msg=f'satiation: {val}')
            self.assertFalse(clock.satiated, msg=f'satiation: {val}')
            self.assertFalse(clock.hungry, msg=f'satiation: {val}')
            self.assertFalse(clock.very_hungry, msg=f'satiation: {val}')
            self.assertFalse(clock.starving, msg=f'satiation: {val}')

    def test_satiated(self):

        clock = HungerClock(rate=1, satiation=12)

        for val in (11, 10, 9, 8):
            clock.satiation = val
            self.assertFalse(clock.full, msg=f'satiation: {val}')
            self.assertTrue(clock.satiated, msg=f'satiation: {val}')
            self.assertFalse(clock.hungry, msg=f'satiation: {val}')
            self.assertFalse(clock.very_hungry, msg=f'satiation: {val}')
            self.assertFalse(clock.starving, msg=f'satiation: {val}')

    def test_hungry(self):

        clock = HungerClock(rate=1, satiation=12)

        for val in (7, 6, 5, 4):
            clock.satiation = val
            self.assertFalse(clock.full, msg=f'satiation: {val}')
            self.assertFalse(clock.satiated, msg=f'satiation: {val}')
            self.assertTrue(clock.hungry, msg=f'satiation: {val}')
            self.assertFalse(clock.very_hungry, msg=f'satiation: {val}')
            self.assertFalse(clock.starving, msg=f'satiation: {val}')

    def test_very_hungry(self):

        clock = HungerClock(rate=1, satiation=12)

        for val in (3, 2):
            clock.satiation = val
            self.assertFalse(clock.full, msg=f'satiation: {val}')
            self.assertFalse(clock.satiated, msg=f'satiation: {val}')
            self.assertFalse(clock.hungry, msg=f'satiation: {val}')
            self.assertTrue(clock.very_hungry, msg=f'satiation: {val}')
            self.assertFalse(clock.starving, msg=f'satiation: {val}')

    def test_starving(self):

        clock = HungerClock(rate=1, satiation=12)

        for val in (1,):
            clock.satiation = val
            self.assertFalse(clock.full, msg=f'satiation: {val}')
            self.assertFalse(clock.satiated, msg=f'satiation: {val}')
            self.assertFalse(clock.hungry, msg=f'satiation: {val}')
            self.assertFalse(clock.very_hungry, msg=f'satiation: {val}')
            self.assertTrue(clock.starving, msg=f'satiation: {val}')

    def test_clock_state(self):

        clock = HungerClock(rate=1, satiation=12)
        self.assertEqual('full', clock.state)

        for val in (11, 10, 9, 8):
            clock.satiation = val
            self.assertEqual('satiated', clock.state, msg=f'satiation: {val}')

        for val in (7, 6, 5, 4):
            clock.satiation = val
            self.assertEqual('hungry', clock.state, msg=f'satiation: {val}')

        for val in (3, 2):
            clock.satiation = val
            self.assertEqual('very hungry', clock.state, msg=f'satiation: {val}')

        for val in (1,):
            clock.satiation = val
            self.assertEqual('starving', clock.state, msg=f'satiation: {val}')
