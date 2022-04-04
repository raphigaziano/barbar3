from unittest.mock import patch

from .base import BaseFunctionalTestCase
from barbarian.actions import Action, ActionType

from barbarian.systems.inventory import (
    get_items, drop_items, equip_item,
)


class TestInventory(BaseFunctionalTestCase):

    def get_action(self, a, d=None):
        return Action(ActionType.GET_ITEM, a, data=d)

    def drop_action(self, a, d=None):
        return Action(ActionType.DROP_ITEM, a, data=d)

    def equip_action(self, a, i):
        return Action(ActionType.EQUIP_ITEM, a, i)

    def test_get_item_with_selection(self):

        level = self.build_dummy_level()
        first_item = self.spawn_item(0, 0, 'health_potion')
        level.items.add_e(first_item)
        second_item = self.spawn_item(0, 0, 'scroll_blink')
        level.items.add_e(second_item)
        third_item = self.spawn_item(0, 0, 'scroll_teleport')
        level.items.add_e(third_item)

        actor = self.spawn_actor(0, 0, 'player')
        action = self.get_action(
            actor, {'item_id_list': [first_item._id, third_item._id]})

        self.assertEqual(3, len(level.items))
        self.assertEqual(0, len(actor.inventory.items))

        self.assert_action_accepted(get_items, action, level)

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
        second_item = self.spawn_item(0, 0, 'scroll_blink')
        third_item = self.spawn_item(0, 0, 'scroll_teleport')

        actor = self.spawn_actor(0, 0, 'player')
        for item in [first_item, second_item, third_item]:
            item.remove_component('pos')
            actor.inventory.items.append(item)

        action = self.get_action(
            actor, {'item_id_list': [first_item._id, third_item._id]})

        self.assertEqual(0, len(level.items))
        self.assertEqual(3, len(actor.inventory.items))

        self.assert_action_accepted(drop_items, action, level)

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

        self.assert_action_accepted(get_items, action, level)

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

        self.assert_action_rejected(get_items, action, level)

        self.assertEqual(0, len(level.items))
        self.assertEqual(0, len(actor.inventory.items))

    def test_drop_item_all(self):

        level = self.build_dummy_level()
        actor = self.spawn_actor(0, 0, 'player')
        for _ in range(2):
            item = self.spawn_item(0, 0, 'scroll_blink')
            item.remove_component('pos')
            actor.inventory.items.append(item)

        action = self.drop_action(actor)

        self.assertEqual(0, len(level.items))
        self.assertEqual(2, len(actor.inventory.items))

        self.assert_action_accepted(drop_items, action, level)

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

        self.assert_action_rejected(drop_items, action, level)

        self.assertEqual(0, len(level.items))
        self.assertEqual(0, len(actor.inventory.items))

    def test_equipped_items_are_unequipped_before_being_dropped(self):

        def _mock_rm(actor, slot):
            actor.inventory.slots[slot] = None
            return True

        with patch(
            'barbarian.systems.inventory._unequip_item', wraps=_mock_rm
        ) as mock_rm_item:

            level = self.build_dummy_level()
            actor = self.spawn_actor(0, 0, 'player')
            item = self.spawn_item(0, 0, 'chainmail')
            item.remove_component('pos')
            actor.inventory.items.append(item)
            actor.inventory.slots['armor'] = item

            action = self.drop_action(actor)
            self.assert_action_accepted(drop_items, action, level)
            mock_rm_item.assert_called_with(actor, 'armor')
            self.assertIsNone(actor.inventory.slots['armor'])

    def test_no_drop_if_item_cannot_be_unequipped(self):

        def _mock_rm(actor, slot):
            return False

        with patch(
            'barbarian.systems.inventory._unequip_item', wraps=_mock_rm
        ) as mock_rm_item:

            level = self.build_dummy_level()
            actor = self.spawn_actor(0, 0, 'player')
            item = self.spawn_item(0, 0, 'chainmail')
            item.remove_component('pos')
            actor.inventory.items.append(item)
            actor.inventory.slots['armor'] = item

            action = self.drop_action(actor)
            self.assert_action_rejected(drop_items, action, level)
            mock_rm_item.assert_called_with(actor, 'armor')
            self.assertEqual(item, actor.inventory.slots['armor'])

    def test_equip_item(self):

        actor = self.spawn_actor(0, 0, 'player')
        item = self.spawn_item(0, 0, 'sword')
        actor.inventory.items.append(item)

        equip_action = self.equip_action(actor, item)
        self.assert_action_accepted(equip_item, equip_action)

        self.assertIn(item, actor.inventory.items)
        self.assertEqual(item, actor.inventory.slots['weapon'])

    @patch('barbarian.systems.inventory._unequip_item')
    def test_equip_item_replace_already_equipped(self, mock_rm_item):

        actor = self.spawn_actor(0, 0, 'player')
        already_equipped = self.spawn_item(0, 0, 'sword')
        actor.inventory.items.append(already_equipped)
        actor.inventory.slots['weapon'] = already_equipped

        self.assertEqual(already_equipped, actor.inventory.slots['weapon'])

        replacing_item = self.spawn_item(0, 0, 'sword')
        actor.inventory.items.append(replacing_item)

        equip_action = self.equip_action(actor, replacing_item)
        self.assert_action_accepted(equip_item, equip_action)

        mock_rm_item.assert_called_with(actor, 'weapon')

        self.assertIn(already_equipped, actor.inventory.items)
        self.assertIn(replacing_item, actor.inventory.items)
        self.assertEqual(replacing_item, actor.inventory.slots['weapon'])

    def test_cannot_replace_unequipable_item(self):

        def _mock_rm(actor, slot):
            return False

        with patch(
            'barbarian.systems.inventory._unequip_item', wraps=_mock_rm
        ) as mock_rm_item:

            actor = self.spawn_actor(0, 0, 'player')
            already_equipped = self.spawn_item(0, 0, 'sword')
            actor.inventory.items.append(already_equipped)
            actor.inventory.slots['weapon'] = already_equipped

            replacing_item = self.spawn_item(0, 0, 'sword')
            actor.inventory.items.append(replacing_item)

            equip_action = self.equip_action(actor, replacing_item)
            self.assert_action_rejected(equip_item, equip_action)

            mock_rm_item.assert_called_with(actor, 'weapon')

            self.assertIn(already_equipped, actor.inventory.items)
            self.assertIn(replacing_item, actor.inventory.items)
            self.assertEqual(already_equipped, actor.inventory.slots['weapon'])

    def test_equip_item_not_in_inventory(self):

        actor = self.spawn_actor(0, 0, 'player')
        item = self.spawn_item(0, 0, 'sword')

        equip_action = self.equip_action(actor, item)
        self.assertRaises(AssertionError, equip_item, equip_action)

    def test_equip_non_equipable_item(self):

        actor = self.spawn_actor(0, 0, 'player')
        item = self.spawn_item(0, 0, 'health_potion')
        item.remove_component('equipable')
        actor.inventory.items.append(item)

        equip_action = self.equip_action(actor, item)
        self.assertRaises(AssertionError, equip_item, equip_action)
