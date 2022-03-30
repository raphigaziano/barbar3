from unittest.mock import patch

from .base import BaseFunctionalTestCase
from barbarian.actions import Action, ActionType
from barbarian.events import Event, EventType

from barbarian.systems.stats import inflict_damage, heal


class TestInflictDmg(BaseFunctionalTestCase):

    def damage_action(self, a, t, dmg):
        return Action.inflict_dmg(a, t, {'dmg': dmg})

    def test_inflict_damage(self):
        hurter = self.spawn_actor(0, 0, 'player')
        hurted = self.spawn_actor(0, 0, 'orc')

        # starting hp should be 3 for orcs

        dmg_action = self.damage_action(hurter, hurted, 2)
        self.assert_action_accepted(inflict_damage, dmg_action)
        self.assertEqual(1, hurted.health.hp)
        self.assertFalse(hurted.health.is_dead)

        # hp can go in the negative (at least for now)

        dmg_action = self.damage_action(hurter, hurted, 2)
        self.assert_action_accepted(inflict_damage, dmg_action)
        self.assertEqual(-1, hurted.health.hp)
        self.assertTrue(hurted.health.is_dead)

    def test_negative_damage_is_not_allowed(self):
        hurter = self.spawn_actor(0, 0, 'player')
        hurted = self.spawn_actor(0, 0, 'orc')

        dmg_action = self.damage_action(hurter, hurted, -2)
        self.assertRaises(ValueError, inflict_damage, dmg_action)

    @patch.object(Event, 'emit')
    def test_death_event_if_hp_fall_below_zero(self, mock_emit):

        hurter = self.spawn_actor(0, 0, 'player')
        hurted = self.spawn_actor(0, 0, 'orc')

        # starting hp should be 3 for orcs

        dmg_action = self.damage_action(hurter, hurted, 10)
        self.assert_action_accepted(inflict_damage, dmg_action)

        mock_emit.assert_called_with(
            EventType.ACTOR_DIED, msg=f'{hurted.name} is dead',
            event_data={'actor': hurted, 'slayer': hurter}
        )

    @patch('barbarian.utils.rng._Rng.roll_dice', return_value=4)
    def test_dmg_dice_string(self, _):

        hurter = self.spawn_actor(0, 0, 'orc')
        hurted = self.spawn_actor(0, 0, 'player')

        # starting hp should be 15 for player

        dmg_action = self.damage_action(hurter, hurted, '1d8')
        self.assert_action_accepted(inflict_damage, dmg_action)
        self.assertEqual(11, hurted.health.hp)


class TestHeal(BaseFunctionalTestCase):

    def heal_action(self, target, amount):
        return Action(
            ActionType.HEAL, None, target, data={'amount': amount})

    def test_heal(self):

        actor = self.spawn_actor(0, 0, 'player')
        actor.health.hp = 1

        heal_action = self.heal_action(actor, 3)
        self.assert_action_accepted(heal, heal_action)
        self.assertEqual(4, actor.health.hp)

    def test_heal_does_not_exceed_max_hp(self):

        actor = self.spawn_actor(0, 0, 'kobold')
        actor.health.hp = 1

        heal_action = self.heal_action(actor, 9999)
        self.assert_action_accepted(heal, heal_action)
        self.assertNotEqual(10000, actor.health.hp)
        self.assertEqual(actor.health.max_hp, actor.health.hp)

    def test_heal_target_already_at_max_health(self):

        actor = self.spawn_actor(0, 0, 'orc')
        self.assertEqual(actor.health.max_hp, actor.health.hp)

        heal_action = self.heal_action(actor, 9999)
        self.assert_action_rejected(heal, heal_action)
        self.assertEqual(actor.health.max_hp, actor.health.hp)

    @patch('barbarian.utils.rng._Rng.roll_dice', return_value=4)
    def test_heal_dice_string(self, _):

        actor = self.spawn_actor(0, 0, 'kobold')
        actor.health.max_hp = 20
        actor.health.hp = 1

        heal_action = self.heal_action(actor, '2D4')
        self.assert_action_accepted(heal, heal_action)
        self.assertEqual(5, actor.health.hp)


class TestRegen(BaseFunctionalTestCase):

    def test_regen_triggered_at_turn_start(self):

        game = self.build_dummy_game()
        game.player.regen.rate = 3
        game.player.health.hp = 1

        self.advance_gameloop()
        self.assertEqual(1, self.game.player.health.hp)

        # tick = regen.rate - 1 (loop yields *before* the end of the
        # turn, so restarting it will increment game ticks and only then
        # process actors)
        self.game.ticks = 2
        self.advance_gameloop()
        self.assertEqual(2, self.game.player.health.hp)

        self.game.ticks = 4
        self.advance_gameloop()
        self.assertEqual(2, self.game.player.health.hp)

        # tick = (rgen.rate * 2) - 1 - see above
        self.game.ticks = 5
        self.advance_gameloop()
        self.assertEqual(3, self.game.player.health.hp)

        # tick = (rgen.rate * 3) - 1 - see above
        self.game.ticks = 8
        self.advance_gameloop()
        self.assertEqual(4, self.game.player.health.hp)
