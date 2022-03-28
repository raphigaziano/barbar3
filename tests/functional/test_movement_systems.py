from unittest.mock import Mock, patch

from .base import BaseFunctionalTestCase

from barbarian.actions import Action, ActionType
from barbarian.events import Event, EventType

from barbarian.systems.movement import (
    move_actor, xplore, change_level, spot_entities,
    blink, teleport,
)


class TestMoveActor(BaseFunctionalTestCase):

    dummy_map = [
        '#####.####',
        '#........#',
        '#....#...#',
        '#........#',
        '##########',
    ]

    def move_action(self, actor, dx, dy):
        return Action.move(actor, {'dir': (dx, dy)})

    def test_move_actor(self):

        for actor in self.actor_list(4, 2, 'player', 'orc'):

            level = self.build_dummy_level()
            level.actors.add_e(actor)

            move_action = self.move_action(actor, 1, 1)
            self.assert_action_accepted(move_actor, move_action, level)

            self.assertEqual((5, 3), (actor.pos.x, actor.pos.y))

    def test_null_vector(self):

        for actor in self.actor_list(4, 2, 'player', 'kobold'):

            level = self.build_dummy_level()
            level.actors.add_e(actor)

            move_action = self.move_action(actor, 0, 0)
            self.assert_action_accepted(move_actor, move_action, level)

            # Action was accepted, but pos was not modified
            self.assertEqual((4, 2), (actor.pos.x, actor.pos.y))

    def test_move_out_of_bound(self):

        for actor in self.actor_list(5, 0, 'player', 'orc'):

            level = self.build_dummy_level()
            level.actors.add_e(actor)

            move_action = self.move_action(actor, 0, -1)
            self.assert_action_rejected(move_actor, move_action, level)

            self.assertEqual((5, 0), (actor.pos.x, actor.pos.y))

    def test_move_blocked_by_wall(self):

        for actor in self.actor_list(1, 1, 'player', 'orc'):

            level = self.build_dummy_level()
            level.actors.add_e(actor)

            move_action = self.move_action(actor, 0, -1)
            self.assert_action_rejected(move_actor, move_action, level)
            self.assertIn("can't move here", move_action.msg)

            self.assertEqual((1, 1), (actor.pos.x, actor.pos.y))

    def test_move_blocked_by_actor(self):

        for actor in self.actor_list(3, 3, 'player', 'kobold'):

            level = self.build_dummy_level()
            level.actors.add_e(actor)

            blocker = self.spawn_actor(3, 2, 'orc')
            level.actors.add_e(blocker)

            move_action = self.move_action(actor, 0, -1)
            self.assert_action_rejected(move_actor, move_action, level)

            self.assertEqual((3, 3), (actor.pos.x, actor.pos.y))

    @patch('barbarian.systems.props.trigger')
    def test_move_blocked_by_prop(self, _):

        for actor in self.actor_list(3, 3, 'player', 'orc'):

            level = self.build_dummy_level()
            level.actors.add_e(actor)

            prop = self.spawn_prop(3, 2, 'door')
            level.props.add_e(prop)

            move_action = self.move_action(actor, 0, -1)
            self.assert_action_rejected(move_actor, move_action, level)

            self.assertEqual((3, 3), (actor.pos.x, actor.pos.y))

    @patch('barbarian.components.actor.Fov.compute')
    def test_fov_recompute_no_fov(self, mock_fov_compute):

        level = self.build_dummy_level()
        actor = self.spawn_actor(4, 2, 'kobold')
        level.actors.add_e(actor)

        move_action = self.move_action(actor, 1, 1)
        move_actor(move_action, level)

        mock_fov_compute.assert_not_called()

    @patch('barbarian.components.actor.Fov.compute')
    def test_fov_recompute_has_fov_not_player(self, mock_fov_compute):

        level = self.build_dummy_level()
        # Spawn a player to get a fov, but unset his player flag 
        # for the test
        actor = self.spawn_actor(4, 2, 'player')
        actor.actor.is_player = False
        level.actors.add_e(actor)

        move_action = self.move_action(actor, 1, 1)
        move_actor(move_action, level)

        mock_fov_compute.assert_called_once_with(
            level, actor.pos.x, actor.pos.y, update_level=False)

    @patch('barbarian.components.actor.Fov.compute')
    def test_fov_recompute_has_fov_and_player(self, mock_fov_compute):

        level = self.build_dummy_level()
        actor = self.spawn_actor(4, 2, 'player')
        level.actors.add_e(actor)

        move_action = self.move_action(actor, 1, 1)
        move_actor(move_action, level)

        mock_fov_compute.assert_called_once_with(
            level, actor.pos.x, actor.pos.y, update_level=True)

    @patch('barbarian.components.actor.Fov.compute')
    @patch('barbarian.systems.movement.spot_entities')
    def test_no_spot_entities_if_no_fov(self, mock_spot, _):

        level = self.build_dummy_level()
        actor = self.spawn_actor(4, 2, 'kobold')
        level.actors.add_e(actor)

        move_action = self.move_action(actor, 1, 1)
        move_actor(move_action, level)

        mock_spot.assert_not_called()

    @patch('barbarian.components.actor.Fov.compute')
    @patch('barbarian.systems.movement.spot_entities')
    def test_spot_entities_if_has_fov(self, mock_spot, _):

        level = self.build_dummy_level()
        actor = self.spawn_actor(4, 2, 'player')
        level.actors.add_e(actor)

        move_action = self.move_action(actor, 1, 1)
        move_actor(move_action, level)

        mock_spot.assert_called_once_with(actor, level)

    def test_attack_actor_on_dest_cell(self):

        for actor in self.actor_list(4, 2, 'player', 'orc'):

            level = self.build_dummy_level()
            level.actors.add_e(actor)

            target = self.spawn_actor(5, 3, 'kobold')
            level.actors.add_e(target)

            move_action = self.move_action(actor, 1, 1)
            new_action = self.assert_action_rejected(
                move_actor, move_action, level)

            self.assertIsNotNone(new_action)
            self.assertEqual(ActionType.ATTACK, new_action.type)
            self.assertEqual(actor, new_action.actor)
            self.assertEqual(target, new_action.target)

    @patch(
        'barbarian.systems.props.trigger' ,
        return_value=Action(type=ActionType.IDLE, data='DUMMY_DATA'))
    def test_trigger_on_enter_props(self, mock_trigger):

        for actor in self.actor_list(4, 2, 'player', 'kobold'):

            mock_trigger.reset_mock()

            level = self.build_dummy_level()
            level.actors.add_e(actor)

            prop = self.spawn_prop(5, 3, 'trap')
            level.props.add_e(prop)

            move_action = self.move_action(actor, 1, 1)
            new_action = self.assert_action_accepted(
                move_actor, move_action, level)

            mock_trigger.assert_called_once_with(actor, prop)

            self.assertIsNotNone(new_action)
            self.assertEqual(ActionType.IDLE, new_action.type)
            self.assertEqual('DUMMY_DATA', new_action.data)

    @patch(
        'barbarian.systems.props.trigger' ,
        return_value=Action(type=ActionType.IDLE, data='DUMMY_DATA'))
    def test_trigger_on_bump_props(self, mock_trigger):

        for actor in self.actor_list(4, 2, 'player', 'orc'):

            mock_trigger.reset_mock()

            level = self.build_dummy_level()
            level.actors.add_e(actor)

            prop = self.spawn_prop(5, 3, 'door')
            level.props.add_e(prop)

            move_action = self.move_action(actor, 1, 1)
            new_action = self.assert_action_rejected(
                move_actor, move_action, level)

            mock_trigger.assert_called_once_with(actor, prop)

            self.assertIsNotNone(new_action)
            self.assertEqual(ActionType.IDLE, new_action.type)
            self.assertEqual('DUMMY_DATA', new_action.data)


class TestXplore(BaseFunctionalTestCase):

    dummy_map = [
        '##########',
        '#.#......#',
        '#.######.#',
        '#........#',
        '##########',
    ]

    def xplore_action(self, actor):
        return Action(type=ActionType.XPLORE, actor=actor)

    def test_xplore(self):

        level = self.build_dummy_level()
        actor = self.spawn_actor(1, 1, 'player')
        level.enter(actor)

        xplore_action = self.xplore_action(actor)
        new_action = self.assert_action_accepted(
            xplore, xplore_action, level)

        self.assertEqual(ActionType.MOVE, new_action.type)
        self.assertEqual({'dir': (0, 1)}, new_action.data)

    def test_xplore_no_fov(self):

        level = self.build_dummy_level()
        actor = self.spawn_actor(1, 1, 'kobold')
        level.enter(actor)

        xplore_action = self.xplore_action(actor)
        new_action = self.assert_action_rejected(
            xplore, xplore_action, level)

        self.assertIsNone(new_action)

    def test_level_fully_explored_actor_is_not_player(self):

        level = self.build_dummy_level()
        # Spawn a player to get a fov, but unset his player flag 
        # for the test
        actor = self.spawn_actor(1, 1, 'player')
        actor.actor.is_player = False

        level.enter(actor)

        for x, y, _ in level.map:
            actor.fov.explored.add((x, y))

        xplore_action = self.xplore_action(actor)
        new_action = self.assert_action_rejected(
            xplore, xplore_action, level)

        self.assertIsNone(new_action)

    def test_level_fully_explored_actor_is_player(self):
        # This is almost the same as the test above, except
        # that explored cells are retrieved differently if
        # actor == player

        level = self.build_dummy_level()
        actor = self.spawn_actor(1, 1, 'player')

        level.enter(actor)

        for x, y, _ in level.map:
            level.explored.add((x, y))

        xplore_action = self.xplore_action(actor)
        new_action = self.assert_action_rejected(
            xplore, xplore_action, level)

        self.assertIsNone(new_action)


@patch('barbarian.world.World')
class TestChangeLevel(BaseFunctionalTestCase):

    dummy_map = [
        '#####.####',
        '#........#',
        '#....#...#',
        '#........#',
        '##########',
    ]

    def change_action(self, dir_):
        return Action(ActionType.CHANGE_LEVEL, data={'dir': dir_})

    def test_change_level(self, mock_world):

        for actor in self.actor_list(1, 1, 'player', 'kobold'):

            for dir_, delta in (('down', 1), (None, 0), ('up', -1)):

                mock_world.reset_mock()

                change_l_action = self.change_action(dir_)
                self.assert_action_accepted(
                    change_level, change_l_action, mock_world, actor)

                mock_world.change_level.assert_called_once_with(
                    delta, actor, False)

    def test_cant_go_up_if_on_first_level(self, mock_world):

        for actor in self.actor_list(1, 1, 'player', 'orc'):

            mock_world.current_depth = 1

            change_l_action = self.change_action('up')
            self.assert_action_rejected(
                change_level, change_l_action, mock_world, actor)

            mock_world.change_level.assert_not_called()


@patch.object(Event, 'emit')
class TestSpotEntities(BaseFunctionalTestCase):

    dummy_map = [
        '#####.####',
        '#........#',
        '#....#...#',
        '#........#',
        '##########',
    ]

    def test_spot_entities(self, mock_emit):

        level = self.build_dummy_level()
        actor = self.spawn_actor(4, 2, 'player')

        a_to_spot = self.spawn_actor(1, 4, 'orc')
        level.actors.add_e(a_to_spot)

        p_to_spot = self.spawn_prop(3, 4, 'trap')
        level.props.add_e(p_to_spot)

        level.enter(actor)

        spot_entities(actor, level)

        self.assertEqual(2, mock_emit.call_count)
        mock_emit.assert_any_call(
            EventType.ACTOR_SPOTTED,
            event_data={'actor': actor, 'target': a_to_spot})
        mock_emit.assert_any_call(
            EventType.ACTOR_SPOTTED,
            event_data={'actor': actor, 'target': p_to_spot})

    def test_spot_entities_no_fov(self, mock_emit):

        level = self.build_dummy_level()
        actor = self.spawn_actor(4, 2, 'kobold')

        a_to_spot = self.spawn_actor(1, 4, 'orc')
        level.actors.add_e(a_to_spot)

        p_to_spot = self.spawn_prop(3, 4, 'trap')
        level.props.add_e(p_to_spot)

        level.enter(actor)

        self.assertRaises(AssertionError, spot_entities, actor, level)

        mock_emit.assert_not_called()

    def test_no_spot_entities_not_in_los(self, mock_emit):

        level = self.build_dummy_level()
        actor = self.spawn_actor(4, 2, 'player')

        # Actor hidden on the other side of the central pillar
        a_to_spot = self.spawn_actor(6, 2, 'player')
        level.actors.add_e(a_to_spot)

        level.enter(actor)

        spot_entities(actor, level)

        mock_emit.assert_not_called()

    def test_no_spot_entities_out_of_fov_range(self, mock_emit):

        level = self.build_dummy_level()
        actor = self.spawn_actor(4, 2, 'player')
        actor.fov.range = 2

        a_to_spot = self.spawn_actor(1, 1, 'kobold')
        level.actors.add_e(a_to_spot)

        level.enter(actor)

        spot_entities(actor, level)

        mock_emit.assert_not_called()


class TestBlink(BaseFunctionalTestCase):

    dummy_map = (
        '###########',
        '#.........#',
        '#..+......#',  # spawn door at 3, 2
        '#.........#',  # spawn player at 5, 3
        '#..#......#',  # wall at 3, 4
        '#......o..#',  # orc at 7, 5
        '###########',
    )
    valid_cells = (
        (3, 1), (4, 1), (5, 1), (6, 1), (7, 1),
        (7, 2),
        (2, 3), (3, 3), (7, 3), (8, 3),
        (7, 4),
        (3, 5), (4, 5), (5, 5), (6, 5)
    )

    def blink_action(self, actor):
        return Action(ActionType.BLINK, actor=actor)

    def test_blink(self):

        for _ in range(200):

            level = self.build_dummy_level()
            actor = self.spawn_actor(5, 3, 'player')
            actor.fov.range = 3
            level.enter(actor)
            actor.fov.compute(level, actor.pos.x, actor.pos.y)

            action = self.blink_action(actor)
            self.assert_action_accepted(blink, action, level)

            pt = (actor.pos.x, actor.pos.y)
            self.assertIn(pt, self.valid_cells)

    def test_blink_recompute_fov(self):

        level = self.build_dummy_level()
        actor = self.spawn_actor(5, 3, 'player')

        actor.fov.compute(level, actor.pos.x, actor.pos.y)

        with patch('barbarian.components.actor.Fov.compute') as mock_fov:
            action = self.blink_action(actor)
            self.assert_action_accepted(blink, action, level)

            mock_fov.assert_called_once()

    def test_blink_no_fov(self):

        level = self.build_dummy_level()
        actor = self.spawn_actor(5, 3, 'player')
        actor.remove_component('fov')

        action = self.blink_action(actor)
        self.assert_action_rejected(blink, action, level)


class TestTeleport(BaseFunctionalTestCase):

    dummy_map = (
        '###########',
        '#+........#',  # spawn door at 1, 1
        '#.......o.#',  # spawn orc at 8, 2
        '#.........#',  # spawn player at 5, 3
        '#.........#',
        '#.#.....#.#',  # wall at 2, 5 & 8, 5
        '###########',
    )
    valid_cells = (
        (2, 1), (3, 1), (4, 1), (6, 1), (7, 1), (8, 1), (9, 1),
        (1, 2), (2, 2), (3, 2), (7, 2), (9, 2),
        (1, 3), (2, 3), (8, 3), (9, 3),
        (1, 4), (2, 4), (3, 4), (7, 4), (8, 4), (9, 4),
        (1, 5), (3, 5), (4, 5), (6, 5), (7, 5), (9, 5)
    )

    def teleport_action(self, actor):
        return Action(ActionType.TELEPORT, actor=actor)

    def test_teleport(self):

        for _ in range(200):

            level = self.build_dummy_level()
            actor = self.spawn_actor(5, 3, 'player')
            actor.fov.range = 2
            level.enter(actor)
            actor.fov.compute(level, actor.pos.x, actor.pos.y)

            action = self.teleport_action(actor)
            self.assert_action_accepted(teleport, action, level)

            pt = (actor.pos.x, actor.pos.y)
            self.assertIn(pt, self.valid_cells)

    def test_teleport_recompute_fov(self):

        level = self.build_dummy_level()
        actor = self.spawn_actor(5, 3, 'player')
        actor.fov.range = 3

        actor.fov.compute(level, actor.pos.x, actor.pos.y)

        with patch('barbarian.components.actor.Fov.compute') as mock_fov:
            action = self.teleport_action(actor)
            self.assert_action_accepted(teleport, action, level)

            mock_fov.assert_called_once()

    def test_teleport_no_fov(self):

        level = self.build_dummy_level()
        actor = self.spawn_actor(5, 3, 'player')
        actor.remove_component('fov')

        action = self.teleport_action(actor)
        self.assert_action_rejected(teleport, action, level)
