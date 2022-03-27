from unittest.mock import Mock, patch

from .base import BaseFunctionalTestCase
from barbarian.actions import Action, ActionType

from barbarian.systems.items import get_item, drop_item


class TestItems(BaseFunctionalTestCase):

    def get_action(self, a, d=None):
        return Action(ActionType.GET_ITEM, a, data=d)

    def drop_action(self, a, d=None):
        return Action(ActionType.DROP_ITEM, a, data=d)

    def test_get_item_with_selection(self):

        level = self.build_dummy_level()
        first_item = self.spawn_item(0, 0, 'health_potion')
        level.items.add_e(first_item)
        second_item = self.spawn_item(0, 0, 'scroll_of_doom')
        level.items.add_e(second_item)
        third_item = self.spawn_item(0, 0, 'scroll_of_woop')
        level.items.add_e(third_item)

        actor = self.spawn_actor(0, 0, 'player')
        action = self.get_action(
            actor, {'item_id_list': [first_item._id, third_item._id]})

        self.assertEqual(3, len(level.items))
        self.assertEqual(0, len(actor.inventory.items))

        self.assert_action_accepted(get_item, action, level)

        self.assertEqual(1, len(level.items))
        self.assertEqual(2, len(actor.inventory.items))

        # Selected items lost pos and in inventory
        for item in (first_item, third_item):
            self.assertIsNone(item.pos)
            self.assertIn(item, actor.inventory.items)
            self.assertNotIn(item, level.items[actor.pos.x, actor.pos.y])

        # Second item left untouched and still stored on the level
        self.assertIsNotNone(second_item.pos)
        self.assertIn(second_item, level.items[actor.pos.x, actor.pos.y])
        self.assertNotIn(second_item, actor.inventory.items)

    def test_drop_item_with_selection(self):

        level = self.build_dummy_level()
        first_item = self.spawn_item(0, 0, 'health_potion')
        second_item = self.spawn_item(0, 0, 'scroll_of_doom')
        third_item = self.spawn_item(0, 0, 'scroll_of_woop')

        actor = self.spawn_actor(0, 0, 'player')
        for item in [first_item, second_item, third_item]:
            item.remove_component('pos')
            actor.inventory.items.append(item)

        action = self.get_action(
            actor, {'item_id_list': [first_item._id, third_item._id]})

        self.assertEqual(0, len(level.items))
        self.assertEqual(3, len(actor.inventory.items))

        self.assert_action_accepted(drop_item, action, level)

        self.assertEqual(2, len(level.items))
        self.assertEqual(1, len(actor.inventory.items))

        # Selected items gaine pos dropped on the level
        for item in (first_item, third_item):
            self.assertIsNotNone(item.pos)
            self.assertNotIn(item, actor.inventory.items)
            self.assertIn(item, level.items[actor.pos.x, actor.pos.y])

        # Second item left untouched and still in inventory
        self.assertIsNone(second_item.pos)
        self.assertNotIn(second_item, level.items[actor.pos.x, actor.pos.y])
        self.assertIn(second_item, actor.inventory.items)

    def test_get_item_all(self):

        level = self.build_dummy_level()
        level.items.add_e(self.spawn_item(0, 0, 'health_potion'))
        level.items.add_e(self.spawn_item(0, 0, 'health_potion'))

        actor = self.spawn_actor(0, 0, 'player')

        action = self.get_action(actor)

        self.assertEqual(2, len(level.items))
        self.assertEqual(0, len(actor.inventory.items))

        self.assert_action_accepted(get_item, action, level)

        self.assertEqual(0, len(level.items))
        self.assertEqual(2, len(actor.inventory.items))

        for item in actor.inventory.items:
            self.assertIsNone(item.pos)

    def test_get_item_all_nothing_on_tile(self):

        level = self.build_dummy_level()
        actor = self.spawn_actor(0, 0, 'player')

        action = self.get_action(actor)

        self.assertEqual(0, len(level.items))
        self.assertEqual(0, len(actor.inventory.items))

        self.assert_action_rejected(get_item, action, level)

        self.assertEqual(0, len(level.items))
        self.assertEqual(0, len(actor.inventory.items))

    def test_drop_item_all(self):

        level = self.build_dummy_level()
        actor = self.spawn_actor(0, 0, 'player')
        for _ in range(2):
            item = self.spawn_item(0, 0, 'scroll_of_doom')
            item.remove_component('pos')
            actor.inventory.items.append(item)

        action = self.drop_action(actor)

        self.assertEqual(0, len(level.items))
        self.assertEqual(2, len(actor.inventory.items))

        self.assert_action_accepted(drop_item, action, level)

        self.assertEqual(2, len(level.items))
        self.assertEqual(0, len(actor.inventory.items))

        for item in level.items.all:
            self.assertIsNotNone(item.pos)
            self.assertEqual(actor.pos, item.pos)

    def test_drop_item_all_empty_inventory(self):

        level = self.build_dummy_level()
        actor = self.spawn_actor(0, 0, 'player')

        action = self.drop_action(actor)

        self.assertEqual(0, len(level.items))
        self.assertEqual(0, len(actor.inventory.items))

        self.assert_action_rejected(drop_item, action, level)

        self.assertEqual(0, len(level.items))
        self.assertEqual(0, len(actor.inventory.items))
