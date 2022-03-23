from .base import BaseFunctionalTestCase
from barbarian.actions import Action, ActionType

from barbarian.systems.combat import attack


class TestAttack(BaseFunctionalTestCase):

    def attack_action(self, a, t):
        return Action.attack(a=a, t=t)

    def test_attack(self):
        attacker = self.spawn_actor(0, 0, 'player')  # str: 5
        attacked = self.spawn_actor(0, 0, 'kobold')  # str: 2

        attack_action = self.attack_action(attacker, attacked)
        new_action = self.assert_action_accepted(attack, attack_action)
        self.assertEqual(ActionType.INFLICT_DMG, new_action.type)
        # str 5 - str 2 = dmg 3
        self.assertEqual({'dmg': 3}, new_action.data)

    def test_weaker_attacker_inflicts_at_least_1_dmg(self):
        attacker = self.spawn_actor(0, 0, 'kobold')  # str: 2
        attacked = self.spawn_actor(0, 0, 'player')  # str: 5

        attack_action = self.attack_action(attacker, attacked)
        new_action = self.assert_action_accepted(attack, attack_action)
        self.assertEqual(ActionType.INFLICT_DMG, new_action.type)
        # str 2 - str 5 = dmg -3 => bumped to 1
        self.assertEqual({'dmg': 1}, new_action.data)
