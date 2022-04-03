from unittest.mock import Mock, patch, DEFAULT
import inspect

from .base import BaseFunctionalTestCase
from barbarian.utils.rng import Rng
from barbarian.actions import Action, ActionType
from barbarian.events import Event
from barbarian.map import Map, TileType
from barbarian.genmap.builders import SimpleMapBuilder
from barbarian.settings import MAP_W, MAP_H

from barbarian.game import Game, EndTurn


class BaseGameTest(BaseFunctionalTestCase):

    def get_loop_state(self, gl):
        return inspect.getgeneratorstate(gl)


class TestGame(BaseGameTest):

    # This seems to generate a fastish map.
    seed = '4876877298345515653'

    @patch('barbarian.world.get_map_builder', return_value=SimpleMapBuilder())
    @patch('barbarian.map.Map.compute_bitmask_grid')
    def test_game_start(self, _, __):

        game = Game()
        game.start_game(seed=self.seed)

        # World was intialized
        self.assertIsNotNone(game.world)
        self.assertEqual(
            (MAP_W, MAP_H), (game.world.level_w, game.world.level_h))

        # First level of depth 1 is built
        self.assertIsNotNone(game.world.current_level)
        self.assertIs(game.current_level, game.world.current_level)
        self.assertEqual(1, game.world.current_depth)
        self.assertEqual(1, game.current_level.depth)

        # Actors shortcut points to the current level
        self.assertListEqual(game.actors, game.current_level.actors.all)

        # Player created and entered current level
        self.assertIsNotNone(game.player)
        self.assertIn(game.player, game.actors)

        # State is not empty
        self.assertIsNotNone(game.state)

        # Run flag is set
        self.assertTrue(game.is_running)

        # Gameloop is running
        self.assertIsNotNone(game.gameloop)
        loop_state = self.get_loop_state(game.gameloop)
        self.assertEqual(inspect.GEN_SUSPENDED, loop_state)
        self.assertEqual(1, game.ticks) # Still processing first turn

    @patch('barbarian.world.get_map_builder', return_value=SimpleMapBuilder())
    @patch('barbarian.map.Map.compute_bitmask_grid')
    @patch.object(Rng, 'init_root')
    def test_seed_is_passed_to_root_rng(self, mock_init_root_rng, _, __):
        game = Game()
        game.start_game(self.seed)

        mock_init_root_rng.assert_called_with(self.seed)

    def test_init_rngs(self):

        game = Game()
        game.init_rng(None)

        self.assertIsNotNone(Rng.root)
        self.assertEqual(2, len(Rng._rngs))
        self.assertIn('dungeon', Rng._rngs)
        self.assertIn('spawn', Rng._rngs)

    @patch('barbarian.systems.movement.change_level')
    def test_setting_change_is_repercuted(self, patched_change_level):
        # Temporary regression test (we'll surely need to change
        # the way settings are handled at some point).
        game = Game()

        game.process_set_request({'key': 'MAP_DEBUG', 'val': True})
        action = Action(ActionType.CHANGE_LEVEL)
        game.dispatch_action(action)
        patched_change_level.assert_called_with(
            action, game.world, game.player, debug=True)

        game.process_set_request({'key': 'MAP_DEBUG', 'val': False})
        action = Action(ActionType.CHANGE_LEVEL)
        game.dispatch_action(action)
        patched_change_level.assert_called_with(
            action, game.world, game.player, debug=False)


class TestGameLoop(BaseGameTest):

    dummy_map = (
        '...',
        '...',
        '...',
    )

    def test_basic_turn(self):

        self.build_dummy_game()
        this = self

        class MethodsMock(Mock):
            def __init__(self, *args, **kwargs):
                kwargs['wraps'] = getattr(this.game, kwargs['name'])
                super().__init__(*args, **kwargs)

        with patch.multiple(
            self.game,
            new_callable=MethodsMock,
            begin_turn=DEFAULT, take_turn=DEFAULT, end_turn=DEFAULT,
        ) as mocks:

            self.advance_gameloop()

            # 1 actors => 1 calls
            self.assertEqual(1, mocks['begin_turn'].call_count)
            self.assertEqual(1, mocks['take_turn'].call_count)
            self.assertEqual(1, mocks['end_turn'].call_count)

            # Event queue cleared, turn counter incremented
            self.assertEqual(0, len(Event.queue))
            self.assertEqual(2, self.game.ticks)

        with patch.multiple(
            self.game,
            new_callable=MethodsMock,
            begin_turn=DEFAULT, take_turn=DEFAULT, end_turn=DEFAULT,
        ) as mocks:

            # spawning at 0,0 seems to move the new actor first in the
            # actor queue... We need a scheduler...
            new_actor = self.spawn_actor(0, 0, 'orc')
            self.game.current_level.actors.add_e(new_actor)

            self.advance_gameloop()

            # 2 actors => 2 calls
            self.assertEqual(2, mocks['begin_turn'].call_count)
            self.assertEqual(2, mocks['take_turn'].call_count)
            self.assertEqual(2, mocks['end_turn'].call_count)

            # Event queue cleared, turn counter incremented
            self.assertEqual(0, len(Event.queue))
            self.assertEqual(3, self.game.ticks)

    def test_turn_aborted(self):

        self.build_dummy_game()

        with patch.object(
            self.game, 'take_turn', wraps=self.game.take_turn,
        ) as mock_take_turn:

            with patch.object(
                Game, 'dispatch_action', side_effect=EndTurn()
            ):
                self.advance_gameloop()

                # First turn aborted => only one call
                self.assertEqual(1, mock_take_turn.call_count)

                # Event queue cleared, turn counter incremented
                self.assertEqual(0, len(Event.queue))
                self.assertEqual(2, self.game.ticks)

    def test_take_turn_invalid_player_action(self):

        self.build_dummy_game()

        with patch.object(
            self.game, 'take_turn', wraps=self.game.take_turn,
        ) as mock_take_turn:

            self.advance_gameloop(
                Action(ActionType.USE_PROP, actor=self.game.player, data={})
            )

            # Action rejected => only one call
            self.assertEqual(1, mock_take_turn.call_count)

            # Event queue cleared, turn counter *not* incremented
            self.assertEqual(0, len(Event.queue))
            self.assertEqual(1, self.game.ticks)

    def test_max_recursion_is_caught(self):

        self.build_dummy_game()
        self.game.current_level.actors.add_e(self.spawn_actor(0, 0, 'orc'))

        def reject_action(a):
            a.accept() if a.actor.is_player else a.reject()
            return a

        with patch.object(
            self.game, 'dispatch_action', wraps=reject_action
        ):
            with self.assertLogs('barbarian.game', 'CRITICAL'):
                self.advance_gameloop(
                    Action(ActionType.IDLE, actor=self.game.player))

    def test_log_warning_if_action_cant_be_processed(self):

        self.build_dummy_game()

        # Returning None should simulate a missing match case
        with patch(
            'barbarian.systems.movement.move_actor', return_value=None
        ):
            with self.assertLogs('barbarian.game', 'WARNING'):
                self.advance_gameloop(
                    Action(
                        ActionType.MOVE, actor=self.game.player,
                        data={'dir': (0, 0)})
                )

    def test_player_death_stops_the_loop(self):

        self.build_dummy_game()

        self.advance_gameloop(
            Action.inflict_dmg(Mock(), self.game.player, {'dmg': 9999}))
        self.assertFalse(self.game.is_running)

    # - take_turn ActionError (?)
