import unittest
from unittest.mock import Mock

from barbarian.components.use import (
    Usable, UseTarget, Trigger, PropActivationMode)
from barbarian.actions import ActionType


class TestUsable(unittest.TestCase):

    def test_get_action(self):

        usable = Usable({'type': 'idle'})
        user  = Mock(name='mocked_user')
        usable_entity = Mock(name='mocked_entity', usable=usable)

        action = usable.get_action(user, usable_entity)

        self.assertEqual(ActionType.IDLE, action.type)
        self.assertEqual(user, action.actor)
        self.assertEqual(usable_entity, action.target)

    def test_usable_targets_actor(self):

        usable = Usable({}, target=UseTarget.SELF)
        user  = Mock(name='mocked_user')
        usable_entity = Mock(name='mocked_entity', usable=usable)

        expected = {'actor': user, 'target': usable_entity}
        self.assertDictEqual(
            expected, usable.get_actor_and_target(user, usable_entity))

    def test_usable_targets_self(self):

        usable = Usable({}, target=UseTarget.ACTOR)
        user  = Mock(name='mocked_user')
        usable_entity = Mock(name='mocked_entity', usable=usable)

        expected = {'actor': usable_entity, 'target': user}
        self.assertDictEqual(
            expected, usable.get_actor_and_target(user, usable_entity))

    def test_usable_target_defaults_to_self(self):
        usable = Usable({})
        self.assertEqual(UseTarget.SELF, usable.target)

    def test_new_action(self):

        usable = Usable({'foo': 'bar'}, target=UseTarget.ACTOR)
        new_usable = usable.new_action({'foo': 'baZ', 'data': 'woot'})

        self.assertIsNot(usable, new_usable)
        self.assertDictEqual(
            {'foo': 'baZ', 'data': 'woot'}, new_usable.action_data)

    def test_new_action_trigger(self):
        """ Same as above but with a Trigger component """

        trigger = Trigger(
            {'foo': 'bar'}, 
            target=UseTarget.ACTOR, 
            activation_mode=PropActivationMode.ACTOR_BUMP)
        new_trigger = trigger.new_action({'foo': 'baZ', 'data': 'woot'})

        self.assertIsNot(trigger, new_trigger)
        self.assertDictEqual(
            {'foo': 'baZ', 'data': 'woot'}, new_trigger.action_data)
