from unittest.mock import patch

from .base import BaseFunctionalTestCase
from barbarian.actions import Action
from barbarian.events import Event, EventType

from barbarian.systems.stats import inflict_damage


class TestAttack(BaseFunctionalTestCase):

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
