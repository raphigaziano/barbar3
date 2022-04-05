from unittest.mock import patch
from .base import BaseFunctionalTestCase

from barbarian.utils.rng import Rng
from barbarian.actions import ActionType
from barbarian.systems.ai import tmp_ai


class TestStoopidAi(BaseFunctionalTestCase):

    def _setup_game(self, level_map):
        game = self.build_dummy_game()
        level = self.build_dummy_level(level_map)
        game.world.insert_level(level, replace_current=True)
        return game

    def test_explicit_attack_if_next_to_player(self):

        game = self._setup_game((
            '...',
            '...',
            '...',
        ))
        player = self.spawn_actor(1, 1, 'player')
        game.current_level.enter(player)
        game.player = player
        mob = self.spawn_actor(1, 0, 'kobold')
        game.current_level.enter(mob)

        action = tmp_ai(mob, game)
        self.assertEqual(ActionType.ATTACK, action.type)
        self.assertEqual(mob, action.actor)
        self.assertEqual(player, action.target)

    def test_move_towards_player(self):

        game = self._setup_game((
            '...',
            '...',
            '...',
        ))
        player = self.spawn_actor(0, 0, 'player')
        game.current_level.enter(player)
        game.player = player
        mob = self.spawn_actor(2, 2, 'kobold')
        game.current_level.enter(mob)

        action = tmp_ai(mob, game)
        self.assertEqual(ActionType.MOVE, action.type)
        self.assertEqual(mob, action.actor)
        self.assertEqual((-1, -1), action.data['dir'])

    def test_move_towards_player_path_blocked(self):

        game = self._setup_game((
            '.#..',
            '.o..',
            '.#..',
        ))
        player = self.spawn_actor(0, 1, 'player')
        game.current_level.enter(player)
        game.player = player
        mob = self.spawn_actor(3, 1, 'kobold')
        game.current_level.enter(mob)

        action = tmp_ai(mob, game)
        self.assertEqual(ActionType.MOVE, action.type)
        self.assertEqual(mob, action.actor)
        self.assertEqual((-1, 0), action.data['dir'])

    @patch('barbarian.utils.rng.Rng.choice', wraps=Rng.choice)
    def test_move_towards_player_path_blocked_avoid_other_mobs(self, mock_choice):

        game = self._setup_game((
            '.#..',
            '.o..',
            '.#..',
        ))
        player = self.spawn_actor(0, 1, 'player')
        game.current_level.enter(player)
        game.player = player
        mob = self.spawn_actor(2, 1, 'kobold')
        game.current_level.enter(mob)

        for _ in range(20):
            action = tmp_ai(mob, game)
            self.assertEqual(ActionType.MOVE, action.type)
            self.assertEqual(mob, action.actor)
            self.assertNotEqual((-1, 0), action.data['dir'])

        self.assertGreaterEqual(mock_choice.call_count, 20)

    @patch('barbarian.utils.rng.Rng.choice', wraps=Rng.choice)
    def test_random_move(self, mock_choice):

        game = self._setup_game((
            '...',
            '...',
            '...',
        ))
        mob = self.spawn_actor(1, 1, 'kobold')
        game.current_level.enter(mob)

        for _ in range(20):
            action = tmp_ai(mob, game)
            self.assertEqual(ActionType.MOVE, action.type)
            self.assertEqual(mob, action.actor)

        self.assertGreaterEqual(mock_choice.call_count, 20)

    @patch('barbarian.utils.rng.Rng.choice', wraps=Rng.choice)
    def test_random_move_avoids_occupied_cells(self, mock_choice):

        game = self._setup_game((
            '#.#',
            '#.#',
            '#.#',
        ))
        mob = self.spawn_actor(1, 1, 'kobold')
        game.current_level.enter(mob)

        for _ in range(20):
            action = tmp_ai(mob, game)
            self.assertEqual(ActionType.MOVE, action.type)
            self.assertEqual(mob, action.actor)
            self.assertNotEqual(-1, action.data['dir'][0])
            self.assertNotEqual(1, action.data['dir'][0])

        game = self._setup_game((
            '###',
            '...',
            '###',
        ))
        mob = self.spawn_actor(1, 1, 'kobold')
        game.current_level.enter(mob)

        for _ in range(20):
            action = tmp_ai(mob, game)
            self.assertEqual(ActionType.MOVE, action.type)
            self.assertEqual(mob, action.actor)
            self.assertNotEqual(-1, action.data['dir'][1])
            self.assertNotEqual(1, action.data['dir'][1])

        self.assertGreaterEqual(mock_choice.call_count, 40)

    def test_all_moves_are_blocked(self):

        game = self._setup_game((
            '###',
            '#.#',
            '###',
        ))

        actor = self.spawn_actor(1, 1, 'orc')
        game.current_level.enter(actor)

        action = tmp_ai(actor, game)
        self.assertEqual(ActionType.IDLE, action.type)
