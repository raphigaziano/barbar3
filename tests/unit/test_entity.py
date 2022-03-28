import unittest

from barbarian.entity import Entity
from barbarian.components.base import Component


class TestEntity(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Component.__COMPONENT_MAP__.clear()

        # Register dummy versions of those, as some enity methods 
        # depend on them existing
        class Typed(Component):
            type: str
        class Named(Component):
            name: str

        class Dummy(Component):
            x: int = 0
            y: int = 0

        cls.Named = Named
        cls.Typed = Typed
        cls.Dummy = Dummy

    def setUp(self):
        Entity._id_counter = 0

    def test_id_increment(self):
        self.assertEqual(Entity._id_counter, 0)

        Entity()
        self.assertEqual(Entity._id_counter, 1)

        Entity()
        self.assertEqual(Entity._id_counter, 2)

    def test_add_componenet_instance(self):
        e = Entity()
        e.add_component('dummy', self.Dummy())
        self.assertTrue(hasattr(e, 'dummy'))
        self.assertIsInstance(e.dummy, self.Dummy)

    def test_add_component_by_name(self):
        e = Entity()
        e.add_component('dummy')
        self.assertTrue(hasattr(e, 'dummy'))
        self.assertIsInstance(e.dummy, self.Dummy)

    def test_component_named_after_component_class(self):
        # ie, passing a "custom" name is ignored
        e = Entity()
        e.add_component('my_custom_attr_name', self.Dummy())
        self.assertFalse(hasattr(e, 'my_custom_attr_name'))
        self.assertTrue(hasattr(e, 'dummy'))
        self.assertIsInstance(e.dummy, self.Dummy)

    def test_add_component_by_name_with_dict_arguments(self):
        e = Entity()
        e.add_component('dummy', {"x": 1, 'y': 42})
        self.assertEqual(e.dummy.x, 1)
        self.assertEqual(e.dummy.y, 42)

    def test_add_unregistered_componenets(self):
        e = Entity()
        with self.assertLogs('barbarian.entity', 'WARNING'):
            self.assertRaises(
                KeyError,
                e.add_component, 'idontexist')

    def test_add_component_by_dict_invalid_data(self):
        e = Entity()
        with self.assertLogs('barbarian.entity', 'WARNING'):
            self.assertRaises(
                TypeError,
                e.add_component, 'dummy', {'invalid': 'lol'})

    def test_get_unset_component(self):
        e = Entity()
        self.assertIsNone(e.dummy)
        self.assertRaises(AttributeError, getattr, e, 'foo')

    def test_remove_component(self):
        e = Entity()
        e.add_component('dummy', self.Dummy())
        self.assertIsNotNone(e.dummy)
        e.remove_component('dummy')
        self.assertIsNone(e.dummy)

    def test_remove_unset_component(self):
        e = Entity()
        # This should fail silently
        e.remove_component('dummy')
        self.assertIsNone(e.dummy)

    def test_replace_comopnent(self):
        e = Entity()
        old_c = self.Dummy(x=1, y=2)
        e.add_component('dummy', old_c)

        new_c = self.Dummy(x=3, y=4)
        e.replace_component(new_c)

        self.assertIsNot(old_c, e.dummy)
        self.assertEqual((3, 4), (e.dummy.x, e.dummy.y))

    def test_components_property(self):

        class Dummy2(Component): pass

        e = Entity()
        e.add_component('dummy', self.Dummy())
        e.add_component('dummy2', Dummy2())

        components = list(e.components)
        self.assertListEqual(
            components,
            [('dummy', self.Dummy()), ('dummy2', Dummy2())])

    def test_name_helper(self):

        e = Entity()
        e.add_component('typed', self.Typed(type='entity_type'))
        self.assertEqual('entity_type', e.name)

        e.add_component('named', self.Typed(type='entity_name'))
        self.assertEqual('entity_name', e.name)

    def test_serialize(self):

        class Dummy2(Component):
            __serialize__ = True
            z: int = 3

        e = Entity()
        e.add_component('dummy', self.Dummy())
        e.add_component('dummy2', Dummy2())

        expected = {
            'id': 1,
            'name': '',
            'type': '',
            # dummy is excluded (__serialize__ = False)
            'dummy2': {
                'z': 3
            }
        }
        self.assertDictEqual(expected, e.serialize())

    def test_from_dict(self):

        class Dummy2(Component): pass

        e = Entity.from_dict({
            'dummy': {'x': 1, 'y': 2},
            'dummy2': {}
        })

        self.assertTrue(hasattr(e, 'dummy'))
        self.assertEqual(e.dummy.x, 1)
        self.assertEqual(e.dummy.y, 2)
        self.assertTrue(hasattr(e, 'dummy2'))

