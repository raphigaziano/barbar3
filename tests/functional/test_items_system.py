from unittest.mock import Mock, patch

from .base import BaseFunctionalTestCase
from barbarian.actions import Action, ActionType

from barbarian.systems.items import get_item, drop_item


class TestItems(BaseFunctionalTestCase):

    def test_get_item_all(self):

        level = self.build_dummy_level()
        level.items.add_e(self.spawn_item(0, 0, 'health_potion'))
        level.items.add_e(self.spawn_item(0, 0, 'health_potion'))

        actor = self.spawn_actor(0, 0, 'player')

        action = Action(ActionType.GET_ITEM, actor=actor)

        self.assertEqual(2, len(level.items))
        self.assertEqual(0, len(actor.inventory.items))

        self.assert_action_accepted(get_item, action, level)

        self.assertEqual(0, len(level.items))
        self.assertEqual(2, len(actor.inventory.items))

        for item in actor.inventory.items:
            self.assertIsNone(item.pos)

    def tet_get_item_all_nothing_on_tile(self):

        level = self.build_dummy_level()
        actor = self.spawn_actor(0, 0, 'player')

        action = Action(ActionType.GET_ITEM, actor=actor)

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

        action = Action(ActionType.DROP_ITEM, actor=actor)

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

        action = Action(ActionType.DROP_ITEM, actor=actor)

        self.assertEqual(0, len(level.items))
        self.assertEqual(0, len(actor.inventory.items))

        self.assert_action_rejected(drop_item, action, level)

        self.assertEqual(0, len(level.items))
        self.assertEqual(0, len(actor.inventory.items))
