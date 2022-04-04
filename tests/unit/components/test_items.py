import unittest

from barbarian.components.items import Inventory


class TestInventory(unittest.TestCase):

    def test_serialize(self):

        class DummyItem:
            def __init__(self, name): self.name = name
            def serialize(self): return self.name

        inv = Inventory([DummyItem('item1'), DummyItem('item2')])
        self.assertDictEqual({
            'slots': {
                'weapon': None, 'shield': None,
                'armor': None, 'helmet': None, 'boots': None, 'gloves': None,
            },
            'items': ['item1', 'item2']
        }, inv.serialize())

        equiped_item = DummyItem('equiped_item')
        inv.items.append(equiped_item)
        inv.slots['shield'] = equiped_item
        self.assertDictEqual({
            'slots': {
                'weapon': None, 'shield': 'equiped_item',
                'armor': None, 'helmet': None, 'boots': None, 'gloves': None,
            },
            'items': ['item1', 'item2', 'equiped_item']
        }, inv.serialize())
