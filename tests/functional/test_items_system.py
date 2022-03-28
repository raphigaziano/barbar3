from .base import BaseFunctionalTestCase
from barbarian.actions import Action, ActionType

from barbarian.game import Game
from barbarian.systems.items import use_item


class BaseItemTestCase(BaseFunctionalTestCase):

    def use_action(self, actor, item):
        return Action(ActionType.USE_ITEM, actor, data={'item_id': item._id})


class TestUseItem(BaseItemTestCase):

    def test_use_item(self):

        for actor_type in ('player', 'orc'):
            actor = self.spawn_actor(0, 0, actor_type)
            item = self.spawn_item(0, 0, 'health_potion')
            actor.inventory.items.append(item)

            new_action = self.assert_action_accepted(
                use_item, self.use_action(actor, item))

            self.assertIsNotNone(new_action)
            self.assertEqual(ActionType.HEAL, new_action.type)

    def test_use_item_not_in_inventory(self):

        actor = self.spawn_actor(0, 0, 'kobold')
        item = self.spawn_item(0, 0, 'health_potion')

        self.assertRaises(
            ValueError, use_item, self.use_action(actor, item))

    def test_use_item_not_usable(self):

        actor = self.spawn_actor(0, 0, 'player')
        item = self.spawn_item(0, 0, 'health_potion')
        item.remove_component('usable')
        actor.inventory.items.append(item)

        self.assert_action_rejected(use_item, self.use_action(actor, item))

class TestConsumableItem(BaseItemTestCase):

    def test_charges_depleted(self):

        game = Game()

        actor = self.spawn_actor(0, 0, 'orc')
        item = self.spawn_item(0, 0, 'health_potion')
        item.consumable.charges = 10
        actor.inventory.items.append(item)
        actor.health.hp = 1

        self.assert_action_accepted(
            game.process_action, self.use_action(actor, item))

        self.assertEqual(9, item.consumable.charges)
        self.assertIn(item, actor.inventory.items)

    def test_one_charge_item_removed_from_inventory(self):

        game = Game()

        actor = self.spawn_actor(0, 0, 'orc')
        item = self.spawn_item(0, 0, 'health_potion')
        actor.inventory.items.append(item)
        actor.health.hp = 1

        # Both the use action and the heal action it returns are accepted
        new_action = self.assert_action_accepted(
            game.process_action, self.use_action(actor, item))

        self.assertTrue(new_action.processed)
        self.assertTrue(new_action.valid)

        # Item removed from inventory
        self.assertEqual(0, item.consumable.charges)
        self.assertNotIn(item, actor.inventory.items)

    def test_item_not_consumed_if_action_is_rejected(self):

        game = Game()

        actor = self.spawn_actor(0, 0, 'orc')
        item = self.spawn_item(0, 0, 'health_potion')
        actor.inventory.items.append(item)

        # use action is accepted, but the heal action it returns is not
        new_action = self.assert_action_accepted(
            game.process_action, self.use_action(actor, item))

        self.assertTrue(new_action.processed)
        self.assertFalse(new_action.valid)

        # Item still in  from inventory
        self.assertEqual(1, item.consumable.charges)
        self.assertIn(item, actor.inventory.items)
