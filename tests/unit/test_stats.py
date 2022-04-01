import unittest
from unittest.mock import Mock, patch

from barbarian.actions import ActionType
from barbarian.systems.stats import regenerate


class TestRegen(unittest.TestCase):

    def test_regen(self):
        actor = Mock()
        actor.regen.rate = 1
        actor.regen.amount = 10

        res = regenerate(actor, 1)
        self.assertIsNotNone(res)
        self.assertEqual(ActionType.HEAL, res.type)
        self.assertDictEqual({'amount': 10}, res.data)

    def test_regen_no_regen(self):

        actor = Mock()
        actor.regen = None

        self.assertIsNone(regenerate(actor, 'ignored_param'))

    def test_regen_rate(self):

        actor = Mock()
        actor.regen.rate = 3

        self.assertIsNone(regenerate(actor, 1))
        self.assertIsNone(regenerate(actor, 2))
        self.assertIsNotNone(regenerate(actor, 3))
        self.assertIsNone(regenerate(actor, 4))
        self.assertIsNone(regenerate(actor, 5))
        self.assertIsNotNone(regenerate(actor, 6))
        self.assertIsNone(regenerate(actor, 7))
        self.assertIsNone(regenerate(actor, 8))
        self.assertIsNotNone(regenerate(actor, 9))
        self.assertIsNone(regenerate(actor, 10))

    def test_no_regen_if_too_hungry(self):

        with patch(
            'barbarian.systems.stats.NO_REGEN_HUNGER_STATES', ('starving', )
        ):
            actor = Mock()
            actor.regen.rate = 1
            actor.hunger_clock.state = 'hungry'

            self.assertIsNotNone(regenerate(actor, 1))

            actor.hunger_clock.state = 'starving'
            self.assertIsNone(regenerate(actor, 1))
