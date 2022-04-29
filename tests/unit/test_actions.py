import unittest
from unittest.mock import patch, Mock

from barbarian.actions import Action, ActionType, TargetMode
from barbarian.actions import ActionDataError, UnknownActionTypeError
from barbarian.events import EventType


class TestAction(unittest.TestCase):

    def test_unpacking(self):
        a, t, d = 'a', 't', 'd'
        action = Action('dummy_type', a, t, d)

        ua, ut, ud = action.unpack()

        self.assertTrue(a is ua)
        self.assertTrue(t is ut)
        self.assertTrue(d is ud)

    def test_accept(self):
        action = Action(ActionType.IDLE)
        action.accept()

        self.assertTrue(action.processed)
        self.assertTrue(action.valid)

    def test_reject(self):
        action = Action(ActionType.IDLE)
        action.reject()

        self.assertTrue(action.processed)
        self.assertFalse(action.valid)

    def test_accept_stores_msg(self):
        action = Action(ActionType.IDLE)
        action.accept(msg='Yay!')

        self.assertEqual('Yay!', action.msg)

    def test_reject_stores_msg(self):
        action = Action(ActionType.IDLE)
        action.reject(msg='Ono!')

        self.assertEqual('Ono!', action.msg)


@patch('barbarian.events.Event.emit')
class TestActionEvents(unittest.TestCase):

    def test_action_event_accepted(self, patched_emit):
        action = Action(ActionType.IDLE)
        action.accept(msg='YAY!')

        patched_emit.assert_called_with(
            EventType.ACTION_ACCEPTED,
            msg='YAY!',
            event_data={'type': 'idle', 'actor': None, 'target': None}
        )

        action = Action(
            ActionType.MOVE, actor='a', data={'dir': 'dummy'})
        action.accept()

        patched_emit.assert_called_with(
            EventType.ACTION_ACCEPTED,
            msg='',
            event_data={'type': 'move', 'actor': 'a', 'target': None}
        )

    def test_action_event_rejected(self, patched_emit):
        action = Action(ActionType.IDLE)
        action.reject(msg='ONOES!')

        patched_emit.assert_called_with(
            EventType.ACTION_REJECTED,
            msg='ONOES!',
            event_data={'type': 'idle', 'actor': None, 'target': None}
        )

        action = Action(
            ActionType.MOVE, actor='a', data={'dir': 'dummy'})
        action.reject()

        patched_emit.assert_called_with(
            EventType.ACTION_REJECTED,
            msg='',
            event_data={'type': 'move', 'actor': 'a', 'target': None}
        )


class TestActionHelpers(unittest.TestCase):

    def test_from_dict(self):
        action = Action.from_dict({'type': 'idle'})
        self.assertEqual(action.type, ActionType.IDLE)

        action = Action.from_dict(
            {'type': 'move', 'actor': 'a',
             'data': {'dir': 'dummy'}}
        )
        self.assertEqual(action.type, ActionType.MOVE)
        self.assertEqual(action.actor, 'a')
        self.assertEqual(action.data, {'dir': 'dummy'})

    def test_from_dict_invalid_action_type(self):
        with self.assertLogs('barbarian.actions', 'WARNING'):
            self.assertRaises(
                UnknownActionTypeError, 
                Action.from_dict, {'type': 'invalid'})

    def test_from_dict_invalid_data(self):
        with self.assertLogs('barbarian.actions', 'WARNING'):
            self.assertRaises(
                ActionDataError,
                Action.from_dict, {'type': 'move', 'invalid_key': 'lol'}
            )
            # self.assertRaises(
            #     ActionDataError,
            #     Action.from_dict, 
            #     {'type': 'move', 'data': {'invalid_key': 'wut'}},)

    def test_attack_shortcut(self):
        action = Action.attack(a='a', t='t')
        self.assertEqual(action.type, ActionType.ATTACK)
        self.assertEqual(action.actor, 'a')
        self.assertEqual(action.target, 't')

    def test_move_shortcut(self):
        action = Action.move(a='a', d={'dir': 'dummy'})
        self.assertEqual(action.type, ActionType.MOVE)
        self.assertEqual(action.actor, 'a')
        self.assertEqual(action.data, {'dir': 'dummy'})

    def test_inflict_dmg_shortcut(self):
        action = Action.inflict_dmg(a='a', t='t', d={'dmg': 1})
        self.assertEqual(action.type, ActionType.INFLICT_DMG)
        self.assertEqual(action.actor, 'a')
        self.assertEqual(action.target, 't')
        self.assertEqual(action.data, {'dmg': 1})

    def test_request_input_shortcut(self):
        action = Action.request_input(input_type='lol')
        self.assertEqual(action.type, ActionType.REQUEST_INPUT)
        self.assertIsNone(action.actor)
        self.assertIsNone(action.target)
        self.assertEqual(action.data, {'input_type': 'lol'})

    def test_request_input_shortcut_no_niput_type(self):
        action = Action.request_input()
        self.assertEqual(action.type, ActionType.REQUEST_INPUT)
        self.assertIsNone(action.actor)
        self.assertIsNone(action.target)
        self.assertEqual(action.data, {})


class TestActionTargeting(unittest.TestCase):

    def test_target_mode_usable(self):

        action = Action(ActionType.IDLE, target_mode=TargetMode.USABLE)
        user  = Mock(name='mocked_user')
        usable_entity = Mock(name='mocked_entity')

        action.set_actor_and_target(user, usable_entity)
        self.assertEqual(user, action.actor)
        self.assertEqual(usable_entity, action.target)

    def test_target_mode_actor(self):

        action = Action(ActionType.IDLE, target_mode=TargetMode.ACTOR)
        user  = Mock(name='mocked_user')
        usable_entity = Mock(name='mocked_entity')

        action.set_actor_and_target(user, usable_entity)
        self.assertEqual(usable_entity, action.actor)
        self.assertEqual(user, action.target)

    def test_target_mode_dir(self):

        action = Action(ActionType.IDLE, target_mode=TargetMode.DIR)
        user  = Mock(name='mocked_user')
        usable_entity = Mock(name='mocked_entity')

        action.set_actor_and_target(user, usable_entity)
        self.assertEqual(user, action.actor)
        self.assertIsNone(action.target)

    def test_target_mode_pos(self):

        action = Action(ActionType.IDLE, target_mode=TargetMode.POS)
        user  = Mock(name='mocked_user')
        usable_entity = Mock(name='mocked_entity')

        action.set_actor_and_target(user, usable_entity)
        self.assertEqual(user, action.actor)
        self.assertIsNone(action.target)

    def test_target_mode_defaults_to_usable(self):
        action = Action(ActionType.IDLE)
        self.assertEqual(TargetMode.USABLE, action.target_mode)

    def test_requires_prompt(self):

        action = Action(ActionType.IDLE, target_mode=TargetMode.USABLE)
        self.assertFalse(action.requires_prompt)

        action = Action(ActionType.IDLE, target_mode=TargetMode.ACTOR)
        self.assertFalse(action.requires_prompt)

        action = Action(ActionType.IDLE, target_mode=TargetMode.DIR)
        self.assertTrue(action.requires_prompt)

        action = Action(ActionType.IDLE, target_mode=TargetMode.POS)
        self.assertTrue(action.requires_prompt)

    def test_check_targeting_data(self):

        action = Action(ActionType.IDLE, target_mode=TargetMode.USABLE)
        self.assertTrue(action.check_target_data())

        action = Action(ActionType.IDLE, target_mode=TargetMode.ACTOR)
        self.assertTrue(action.check_target_data())

        action = Action(ActionType.IDLE, target_mode=TargetMode.DIR)
        self.assertFalse(action.check_target_data())
        action.data['dir'] = (1, 1)
        self.assertTrue(action.check_target_data())

        action = Action(ActionType.IDLE, target_mode=TargetMode.POS)
        self.assertFalse(action.check_target_data())
        action.data['pos'] = (1, 1)
        self.assertTrue(action.check_target_data())
