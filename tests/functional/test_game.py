from unittest.mock import Mock, patch
import inspect

from .base import BaseFunctionalTestCase
from barbarian.utils.rng import Rng
from barbarian.actions import Action, ActionType
from barbarian.events import Event
from barbarian.world import World, Level
from barbarian.map import Map, TileType

from barbarian.game import Game, EndTurn
from barbarian.settings import MAP_W, MAP_H


class BaseGameTest(BaseFunctionalTestCase):

    def get_loop_state(self, gl):
        return inspect.getgeneratorstate(gl)


class TestGame(BaseGameTest):

    # This seems to generate a fastish map.
    seed = '4876877298345515653'

    @patch('barbarian.genmap.common.BaseMapBuilder')
    def test_game_start(self, _):

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

        # Actors shortcuts points to the current level
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

    @patch('barbarian.genmap.common.BaseMapBuilder')
    @patch.object(Rng, 'init_root')
    def test_seed_is_passed_to_root_rng(self, mock_init_root_rng, _):
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
        game.process_action(action)
        patched_change_level.assert_called_with(
            action, game.world, game.player, debug=True)

        game.process_set_request({'key': 'MAP_DEBUG', 'val': False})
        action = Action(ActionType.CHANGE_LEVEL)
        game.process_action(action)
        patched_change_level.assert_called_with(
            action, game.world, game.player, debug=False)


class TestGameLoop(BaseGameTest):

    def get_gameloop(self):
        """ Return a minimal game object and return its gameloop """
        self.game = Game()

        map_w, map_h = MAP_W, MAP_H
        world = World(map_w, map_h)
        level = Level(map_w, map_h)
        level.map = Map(
            map_w, map_h,
            [TileType.FLOOR for _ in range(map_w * map_h)]
        )
        level.start_pos = 1, 1
        level.exit_pos = 8, 8
        level.init_fov_map()

        self.game.player = self.spawn_actor(1, 1, 'player')
        level.enter(self.game.player)
        mob = self.spawn_actor(3, 3, 'orc')
        level.actors.add_e(mob)

        world.insert_level(level)
        self.game.world = world

        self.game.is_running = True

        self.game.start_gameloop()
        return self.game.gameloop

    def test_basic_turn(self):

        gl = self.get_gameloop()

        with patch.object(
            self.game, 'take_turn', wraps=self.game.take_turn,
        ) as mock_take_turn:

            gl.send(Action(ActionType.IDLE))

            # 2 actors => 2 calls
            self.assertEqual(2, mock_take_turn.call_count)

            # Event queue cleared, turn counter incremented
            self.assertEqual(0, len(Event.queue))
            self.assertEqual(2, self.game.ticks)

    def test_turn_aborted(self):

        gl = self.get_gameloop()

        with patch.object(
            self.game, 'take_turn', wraps=self.game.take_turn,
        ) as mock_take_turn:

            with patch.object(
                Game, 'process_action', side_effect=EndTurn()
            ):
                gl.send(Action(ActionType.IDLE))

                # First turn aborted => only one call
                self.assertEqual(1, mock_take_turn.call_count)

                # Event queue cleared, turn counter incremented
                self.assertEqual(0, len(Event.queue))
                self.assertEqual(2, self.game.ticks)

    def test_take_turn_invalid_player_action(self):

        gl = self.get_gameloop()

        with patch.object(
            self.game, 'take_turn', wraps=self.game.take_turn,
        ) as mock_take_turn:

            gl.send(
                Action(ActionType.USE_PROP, actor=self.game.player, data={})
            )

            # Action rejected => only one call
            self.assertEqual(1, mock_take_turn.call_count)

            # Event queue *not* cleared, turn counter *not* incremented
            self.assertNotEqual(0, len(Event.queue))
            self.assertEqual(1, self.game.ticks)

    def test_max_recursion_is_caught(self):

        gl = self.get_gameloop()

        def reject_action(a):
            a.accept() if a.actor.is_player else a.reject()
            return a

        with patch.object(
            self.game, 'process_action', wraps=reject_action
        ):
            with self.assertLogs('barbarian.game', 'CRITICAL'):
                gl.send(Action(ActionType.IDLE, actor=self.game.player))

    def test_log_warning_if_action_cant_be_processed(self):

        gl = self.get_gameloop()

        # Returning None should simulate a missing match case
        with patch(
            'barbarian.systems.movement.move_actor', return_value=None
        ):
            with self.assertLogs('barbarian.game', 'WARNING'):
                gl.send(
                    Action(
                        ActionType.MOVE, actor=self.game.player,
                        data={'dir': (0, 0)})
                )

    def test_player_death_stops_the_loop(self):

        gl = self.get_gameloop()

        try:
            gl.send(
                Action.inflict_dmg(Mock(), self.game.player, {'dmg': 9999}))
        except StopIteration:
            # This is handled by the game during normal run.
            pass

        self.assertFalse(self.game.is_running)

    # - take_turn ActionError (?)
