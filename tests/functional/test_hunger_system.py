from unittest.mock import patch, ANY
from .base import BaseFunctionalTestCase

from barbarian.actions import Action, ActionType
from barbarian.events import EventType
from barbarian.systems.hunger import eat


class TestHunger(BaseFunctionalTestCase):

    MAX_SATIATION = 100
    HUNGER_STATES = (
        ('starving', 16),
        ('very hungry', 33),
        ('hungry', 66),
        ('satiated', 95),
    )

    def setUp(self):
        super().setUp()

        max_satiation_patcher = patch(
            'barbarian.components.actor.MAX_HUNGER_SATIATION', self.MAX_SATIATION)
        max_satiation_patcher.start()
        hunger_states_patcher = patch(
            'barbarian.components.actor.HUNGER_STATES', self.HUNGER_STATES)
        hunger_states_patcher.start()

        self.addCleanup(max_satiation_patcher.stop)
        self.addCleanup(hunger_states_patcher.stop)

    def test_no_op_if_no_clock(self):

        game = self.build_dummy_game()
        game.player.remove_component('hunger_clock')

        with patch(
            'barbarian.components.actor.HungerClock.__getattribute__'
        ) as mock_getattr:
            # No touching the hunger clock for a hundred turns
            for _ in range(100):
                self.advance_gameloop()
                mock_getattr.assert_not_called()

    def test_update_clock(self):

        game = self.build_dummy_game()
        game.player.hunger_clock.rate = 5
        game.player.hunger_clock.satiation = 100

        with patch('barbarian.systems.hunger.MAX_HUNGER_SATIATION', 100):

            self.advance_gameloop()
            self.assertEqual(100, game.player.hunger_clock.satiation)

            game.ticks = 4
            self.advance_gameloop()
            self.assertEqual(99, game.player.hunger_clock.satiation)
            self.advance_gameloop()
            self.assertEqual(99, game.player.hunger_clock.satiation)

            game.ticks = 9
            self.advance_gameloop()
            self.assertEqual(98, game.player.hunger_clock.satiation)
            self.advance_gameloop()
            self.assertEqual(98, game.player.hunger_clock.satiation)

            # ...

    def _test_state_change(
            self, game, new_state, mock_emit, *emit_args, **emit_kwargs):

        mock_emit.reset_mock()
        self.advance_gameloop()
        self.assertEqual(new_state, game.player.hunger_clock.state)
        # 1 call for IdleAction accpeted, + 1 for hunger state change
        self.assertEqual(2, mock_emit.call_count)
        mock_emit.assert_called_with(*emit_args, **emit_kwargs)
        mock_emit.reset_mock()
        self.advance_gameloop()
        # No more calls until state changes again (but allowing one for
        # IdleAction acceptance).
        mock_emit.assert_called_once()

    @patch('barbarian.events.Event.emit')
    def test_event_emitted_on_state_change(self, mock_event_emit):

        with patch('barbarian.systems.hunger.MAX_HUNGER_SATIATION', 100):
            game = self.build_dummy_game()
            game.player.hunger_clock.rate = 1
            game.player.hunger_clock.satiation = 100

            self.assertEqual('full', game.player.hunger_clock.state)

            game.player.hunger_clock.satiation = 95
            self._test_state_change(
                game, 'satiated', mock_event_emit,
                EventType.FOOD_STATE_UPDATED,
                msg=ANY,
                event_data={'actor': game.player, 'state': 'satiated'})

            game.player.hunger_clock.satiation = 66
            self._test_state_change(
                game, 'hungry', mock_event_emit,
                EventType.FOOD_STATE_UPDATED,
                msg=ANY,
                event_data={'actor': game.player, 'state': 'hungry'})

            game.player.hunger_clock.satiation = 33
            self._test_state_change(
                game, 'very hungry', mock_event_emit,
                EventType.FOOD_STATE_UPDATED,
                msg=ANY,
                event_data={'actor': game.player, 'state': 'very hungry'})

            # Ensure no starve damage for this test
            with patch('barbarian.utils.rng.Rng.randint', return_value=100):
                game.player.hunger_clock.satiation = 16
                self._test_state_change(
                    game, 'starving', mock_event_emit,
                    EventType.FOOD_STATE_UPDATED,
                    msg=ANY,
                    event_data={'actor': game.player, 'state': 'starving'})

    @patch('barbarian.systems.hunger.HUNGER_DMG', 5)
    def test_starving_damage(self):

        game = self.build_dummy_game()
        game.player.hunger_clock.rate = 1
        game.player.hunger_clock.satiation = 15
        game.player.health.hp = 10

        with patch('barbarian.utils.rng.Rng.randint', return_value=100):
            self.advance_gameloop()
            # cmd roll chance failed, no dmg
            self.assertEqual(10, game.player.health.hp)

        with patch('barbarian.utils.rng.Rng.randint', return_value=1):
            self.advance_gameloop()
            # cmd roll chance passed
            self.assertEqual(5, game.player.health.hp)

            self.advance_gameloop()
            # cmd roll chance passed
            self.assertEqual(0, game.player.health.hp)
            self.assertTrue(game.player.health.is_dead)


class TestEat(BaseFunctionalTestCase):

    def eat_action(self, a, t):
        return Action(ActionType.EAT, actor=a, target=t)

    @patch('barbarian.events.Event.emit')
    def test_eat(self, mock_event_emit):

        actor = self.spawn_actor(0, 0, 'player')
        actor.hunger_clock.satiation = 10
        food_item = self.spawn_item(0, 0, 'food_ration')
        food_item.edible.nutrition = 5

        eat_action = self.eat_action(actor, food_item)
        self.assert_action_accepted(eat, self.eat_action(actor, food_item))

        self.assertEqual(15, actor.hunger_clock.satiation)
        # 1 call for eat action acceptance, + one for hunger_clock status update
        self.assertEqual(2, mock_event_emit.call_count)

    def test_eaction_no_hunger_clock(self):

        actor = self.spawn_actor(0, 0, 'player')
        actor.remove_component('hunger_clock')
        food_item = self.spawn_item(0, 0, 'food_ration')

        eat_action = self.eat_action(actor, food_item)
        self.assertRaises(AssertionError, eat, self.eat_action(actor, food_item))

    @patch('barbarian.systems.hunger._update_hunger_clock')
    def test_eat_clock_full(self, mock_update_clock):

        actor = self.spawn_actor(0, 0, 'player')
        food_item = self.spawn_item(0, 0, 'food_ration')

        eat_action = self.eat_action(actor, food_item)
        self.assert_action_rejected(eat, self.eat_action(actor, food_item))

        mock_update_clock.assert_not_called()
