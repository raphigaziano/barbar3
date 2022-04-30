from unittest.mock import Mock, patch

from .base import BaseFunctionalTestCase
from barbarian.actions import Action, ActionType
from barbarian.events import EventType

from barbarian.systems.props import (
    use_prop, trigger, open_or_close_door
)


class TestUseProp(BaseFunctionalTestCase):

    dummy_map = (
        '#####',
        '#...#',
        '#...#',
        '#...#',
        '#####',
    )

    def use_action(self, actor, d=None):
        d = d or {}
        return Action(ActionType.USE_PROP, actor=actor, data=d)

    def test_use_prop_on_actor_tile(self):

        for actor in self.actor_list(2, 2, 'player', 'orc'):

            level = self.build_dummy_level()
            level.actors.add_e(actor)

            prop = self.spawn_prop(2, 2, 'stairs_up')
            level.props.add_e(prop)

            use_action = self.use_action(actor, {'use_key': 'up'})

            new_action = self.assert_action_accepted(
                use_prop, use_action, level)
            self.assertIsNotNone(new_action)

    def test_use_prop_on_actor_tile_no_prop_here(self):

        for actor in self.actor_list(2, 2, 'player', 'orc'):

            level = self.build_dummy_level()
            level.actors.add_e(actor)

            use_action = self.use_action(actor)

            new_action = self.assert_action_rejected(
                use_prop, use_action, level)
            self.assertIsNone(new_action)

            self.assertIn("can't do that", use_action.msg)

    def test_use_prop_invalid_use_key(self):

        for actor in self.actor_list(2, 2, 'player', 'orc'):

            level = self.build_dummy_level()
            level.actors.add_e(actor)

            prop = self.spawn_prop(2, 2, 'stairs_up')
            level.props.add_e(prop)

            use_action = self.use_action(
                actor, {'use_key': 'butt'})

            new_action = self.assert_action_rejected(
                use_prop, use_action, level)
            self.assertIsNone(new_action)

            self.assertIn("can't do that", use_action.msg)

    def test_use_prop_on_neighbor_cell(self):

        for actor in self.actor_list(2, 2, 'player', 'orc'):

            level = self.build_dummy_level()
            level.actors.add_e(actor)

            prop = self.spawn_prop(2, 3, 'door')
            level.props.add_e(prop)

            use_action = self.use_action(
                actor, {'propx': 2, 'propy': 3})

            new_action = self.assert_action_accepted(
                use_prop, use_action, level)
            self.assertIsNotNone(new_action)

    def test_use_prop_on_neighbor_cell_no_prop_there(self):

        for actor in self.actor_list(2, 2, 'player', 'orc'):

            level = self.build_dummy_level()
            level.actors.add_e(actor)

            use_action = self.use_action(
                actor, {'propx': 2, 'propy': 3})

            new_action = self.assert_action_rejected(
                use_prop, use_action, level)
            self.assertIsNone(new_action)

            self.assertIn("can't do that", use_action.msg)

    def test_use_non_usable_prop(self):

        for actor in self.actor_list(2, 2, 'player', 'orc'):

            level = self.build_dummy_level()
            level.actors.add_e(actor)

            prop = self.spawn_prop(2, 2, 'trap')
            level.props.add_e(prop)

            use_action = self.use_action(actor)

            new_action = self.assert_action_rejected(
                use_prop, use_action, level)
            self.assertIsNone(new_action)

            self.assertIn("can't do that", use_action.msg)


class TestTrigger(BaseFunctionalTestCase):

    def test_door(self):

        for actor in self.actor_list(0, 0, 'player', 'orc'):

            prop = self.spawn_prop(2, 2, 'door')

            triggered_action = trigger(actor, prop)

            self.assertIsNotNone(triggered_action)
            self.assertEqual(actor, triggered_action.actor)
            self.assertEqual(prop, triggered_action.target)
            self.assertEqual(ActionType.OPEN_DOOR, triggered_action.type)

    @patch('barbarian.events.Event.emit')
    def test_trap(self, mocked_event_emit):

        for actor in self.actor_list(0, 0, 'player', 'orc'):

            mocked_event_emit.reset_mock()

            prop = self.spawn_prop(2, 2, 'trap')

            triggered_action = trigger(actor, prop)

            self.assertIsNotNone(triggered_action)
            self.assertEqual(prop, triggered_action.actor)
            self.assertEqual(actor, triggered_action.target)
            self.assertEqual(ActionType.INFLICT_DMG, triggered_action.type)

            mocked_event_emit.assert_called_once_with(
                EventType.ENTITY_CONSUMED,
                data={'entity': prop,
                      'action': prop.trigger.get_action(actor, prop)})

    def test_trap_dont_trigger_if_depleted(self):

        for actor in self.actor_list(0, 0, 'player', 'orc'):

            prop = self.spawn_prop(2, 2, 'trap')
            prop.consumable.charges = 0

            triggered_action = trigger(actor, prop)
            self.assertIsNone(triggered_action)


class OpenCloseDoorTest(BaseFunctionalTestCase):

    dummy_map = ('...', '...', '...')

    def get_door_entity(self, x=0, y=0, opened=False):
        d = self.spawn_prop(x, y, 'door')
        if opened:
            d.physics.blocks = False
            d.physics.blocks_sight = False
            d.usable = d.usable.new_action({'type': 'close_door'})
            d.openable.open = True
        return d

    def open_door(self, a, t=None, d=None):
        return Action(
            ActionType.OPEN_DOOR, actor=a, target=t, data=d or {})

    def close_door(self, a, t=None, d=None):
        return Action(
            ActionType.CLOSE_DOOR, actor=a, target=t, data=d or {})

    def assert_opened(self, door):
        self.assertTrue(door.openable.open)
        self.assertFalse(door.physics.blocks)
        self.assertFalse(door.physics.blocks_sight)
        self.assertEqual('close_door', door.usable.action_data['type'])
        # Fu testing glyph & name

    def assert_closed(self, door):
        self.assertFalse(door.openable.open)
        self.assertTrue(door.physics.blocks)
        self.assertTrue(door.physics.blocks_sight)
        self.assertEqual('open_door', door.usable.action_data['type'])
        # Fu testing glyph & name

    def test_open_door(self):

        for actor in self.actor_list(0, 0, 'player', 'kobold'):

            level = self.build_dummy_level()
            door = self.get_door_entity(opened=False)
            action = self.open_door(actor, door)

            self.assert_action_accepted(
                open_or_close_door, action, level)
            self.assert_opened(door)

    def test_close_door(self):

        for actor in self.actor_list(0, 0, 'player', 'kobold'):

            level = self.build_dummy_level()
            door = self.get_door_entity(opened=True)
            action = self.close_door(actor, door)

            self.assert_action_accepted(
                open_or_close_door, action, level)
            self.assert_closed(door)

    def test_open_close_surrounding_door_with_explicit_direction(self):

        # Spawn door all around actor
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (dx, dy) == (0, 0):
                    continue

                level = self.build_dummy_level()
                actor = self.spawn_actor(1, 1, 'kobold')
                level.enter(actor)
                door = self.get_door_entity(1 + dx, 1 + dy)
                level.props.add_e(door)

                # Open door
                initial_open_action = self.open_door(
                    actor, d={'dir': (dx, dy)})
                new_open_action = open_or_close_door(initial_open_action, level)
                self.assertEqual(new_open_action.type, ActionType.OPEN_DOOR)
                self.assertEqual(new_open_action.target, door)

                self.assert_action_accepted(
                    open_or_close_door, new_open_action, level)

                 # Close door
                initial_close_action = self.close_door(
                    actor, d={'dir': (dx, dy)})
                new_close_action = open_or_close_door(initial_close_action, level)
                self.assertEqual(new_close_action.type, ActionType.CLOSE_DOOR)
                self.assertEqual(new_close_action.target, door)

                self.assert_action_accepted(
                    open_or_close_door, new_close_action, level)

    def test_open_close_surrounding_door_no_explicit_dir(self):

        # Spawn door all around actor
        for x in (0, 1, 2):
            for y in (0, 1, 2):
                if (x, y) == (1, 1):
                    continue

                level = self.build_dummy_level()
                actor = self.spawn_actor(1, 1, 'kobold')
                level.enter(actor)
                door = self.get_door_entity(x, y)
                level.props.add_e(door)

                # Open door
                initial_open_action = self.open_door(actor)
                new_open_action = open_or_close_door(initial_open_action, level)
                self.assertEqual(new_open_action.type, ActionType.OPEN_DOOR)
                self.assertEqual(new_open_action.target, door)

                self.assert_action_accepted(
                    open_or_close_door, new_open_action, level)

                 # Close door
                initial_close_action = self.close_door(actor)
                new_close_action = open_or_close_door(initial_close_action, level)
                self.assertEqual(new_close_action.type, ActionType.CLOSE_DOOR)
                self.assertEqual(new_close_action.target, door)

                self.assert_action_accepted(
                    open_or_close_door, new_close_action, level)

    def test_open_close_surrounding_door_no_surrounding_door(self):

        level = self.build_dummy_level()
        actor = self.spawn_actor(1, 1, 'kobold')
        level.enter(actor)

        # Open door
        initial_open_action = self.open_door(actor)
        self.assert_action_rejected(
            open_or_close_door, initial_open_action, level)

         # Close door
        initial_close_action = self.close_door(actor)
        self.assert_action_rejected(
            open_or_close_door, initial_close_action, level)

    def test_prompt_to_chose_target_door(self):

        # Doors on only two opposite sides
        level = self.build_dummy_level()
        actor = self.spawn_actor(1, 1, 'kobold')
        level.enter(actor)
        door = self.get_door_entity(0, 1)
        level.props.add_e(door)
        door = self.get_door_entity(2, 1)
        level.props.add_e(door)

        # Open door
        initial_open_action = self.open_door(actor)
        new_open_action = open_or_close_door(initial_open_action, level)
        self.assertEqual(new_open_action.type, ActionType.REQUEST_INPUT)
        self.assertEqual(new_open_action.data, {'input_type': 'dir'})

         # Close door
        initial_close_action = self.close_door(actor)
        new_close_action = open_or_close_door(initial_close_action, level)
        self.assertEqual(new_open_action.type, ActionType.REQUEST_INPUT)
        self.assertEqual(new_open_action.data, {'input_type': 'dir'})

        # Doors on every surrounding cell
        level = self.build_dummy_level()
        actor = self.spawn_actor(1, 1, 'kobold')
        level.enter(actor)
        for x in (0, 1, 2):
            for y in (0, 1, 2):
                door = self.get_door_entity(x, y)
                level.props.add_e(door)

        # Open door
        initial_open_action = self.open_door(actor)
        new_open_action = open_or_close_door(initial_open_action, level)
        self.assertEqual(new_open_action.type, ActionType.REQUEST_INPUT)
        self.assertEqual(new_open_action.data, {'input_type': 'dir'})

         # Close door
        initial_close_action = self.close_door(actor)
        new_close_action = open_or_close_door(initial_close_action, level)
        self.assertEqual(new_open_action.type, ActionType.REQUEST_INPUT)
        self.assertEqual(new_open_action.data, {'input_type': 'dir'})

    def test_open_already_opened(self):

        for actor in self.actor_list(0, 0, 'player', 'kobold'):

            level = self.build_dummy_level()
            door = self.get_door_entity(opened=True)
            action = self.open_door(actor, door)

            self.assert_action_rejected(
                open_or_close_door, action, level)
            self.assert_opened(door)
            self.assertIn('already open', action.msg)

    def test_close_already_closed(self):

        for actor in self.actor_list(0, 0, 'player', 'kobold'):

            level = self.build_dummy_level()
            door = self.get_door_entity(opened=False)
            action = self.close_door(actor, door)

            self.assert_action_rejected(open_or_close_door, action, level)
            self.assert_closed(door)
            self.assertIn('already close', action.msg)

    def test_cannot_close_door_if_blocked_by_entity(self):

        for entity_type in ('actors', 'props', 'items'):
            for actor in self.actor_list(0, 0, 'player', 'kobold'):

                level = self.build_dummy_level()
                door = self.get_door_entity(opened=True)
                level.props.add(0, 0, door)

                blocking_entity = Mock()
                blocking_entity.pos.x, blocking_entity.pos.y = 0, 0
                entity_container = getattr(level, entity_type)
                entity_container.add_e(blocking_entity)

                close_action = self.close_door(actor, door)
                self.assert_action_rejected(
                    open_or_close_door, close_action, level)

    @patch('barbarian.components.actor.Fov.compute')
    def test_recompute_fov_actor_has_fov(self, mock_fov_compute):

        level = self.build_dummy_level()
        actor = self.spawn_actor(0, 0, 'player')
        door = self.get_door_entity(opened=False)

        for action in (
                self.open_door(actor, door),
                self.close_door(actor, door)
        ):
            mock_fov_compute.reset_mock()

            self.assert_action_accepted(
                open_or_close_door, action, level)
            mock_fov_compute.assert_called_with(
                level, actor.pos.x, actor.pos.y, update_level=True)

    @patch('barbarian.components.actor.Fov.compute')
    def test_recompute_fov_actor_has_no_fov(self, mock_fov_compute):

        level = self.build_dummy_level()
        actor = self.spawn_actor(0, 0, 'kobold')
        door = self.get_door_entity(opened=False)

        for action in (
                self.open_door(actor, door),
                self.close_door(actor, door)
        ):
            mock_fov_compute.reset_mock()

            self.assert_action_accepted(
                open_or_close_door, action, level)
            mock_fov_compute.assert_not_called()
