import unittest
from unittest.mock import Mock

from barbarian.components.use import (
    Usable, Trigger, PropActivationMode)
from barbarian.actions import ActionType, TargetMode


class TestUsable(unittest.TestCase):

    def test_get_action(self):

        usable = Usable({'type': 'idle'})
        user  = Mock(name='mocked_user')
        usable_entity = Mock(name='mocked_entity', usable=usable)

        action = usable.get_action(user, usable_entity)

        self.assertEqual(ActionType.IDLE, action.type)
        self.assertEqual(user, action.actor)
        self.assertEqual(usable_entity, action.target)

    def test_new_action(self):

        usable = Usable({'foo': 'bar'})
        new_usable = usable.new_action({'foo': 'baZ', 'data': 'woot'})

        self.assertIsNot(usable, new_usable)
        self.assertDictEqual(
            {'foo': 'baZ', 'data': 'woot'}, new_usable.action_data)

    def test_new_action_trigger(self):
        """ Same as above but with a Trigger component """

        trigger = Trigger(
            {'foo': 'bar'},
            activation_mode=PropActivationMode.ACTOR_BUMP)
        new_trigger = trigger.new_action({'foo': 'baZ', 'data': 'woot'})

        self.assertIsNot(trigger, new_trigger)
        self.assertDictEqual(
            {'foo': 'baZ', 'data': 'woot'}, new_trigger.action_data)
