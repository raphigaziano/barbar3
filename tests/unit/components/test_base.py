import unittest

from barbarian.components.base import Component


class BaseComponentTestCase(unittest.TestCase):

    def setUp(self):
        Component.__COMPONENT_MAP__.clear()


class TestComponentMeta(BaseComponentTestCase):

    def test_component_registration(self):

        self.assertEqual(len(Component.__COMPONENT_MAP__), 0)

        class DummyComponent(Component):
            pass

        self.assertEqual(len(Component.__COMPONENT_MAP__), 1)
        self.assertIn('dummycomponent', Component.__COMPONENT_MAP__)
        self.assertIs(
            Component.__COMPONENT_MAP__['dummycomponent'],
            DummyComponent)

        class Another(Component):
            pass

        self.assertEqual(len(Component.__COMPONENT_MAP__), 2)
        self.assertIn('another', Component.__COMPONENT_MAP__)
        self.assertIs(
            Component.__COMPONENT_MAP__['another'],
            Another)

    def test_named_component_registration(self):

        class Dummy(Component):
            __attr_name__ = 'custom_name'
            pass

        self.assertIn('custom_name', Component.__COMPONENT_MAP__)


class TestComponent(BaseComponentTestCase):

    def test_flyweight(self):

        class Dummy(Component):
            __flyweight__ = True
            x: int
            y: int

        # Note: 
        # Name mangling seems to be done according to the current scope
        # instead of the class on which the attribute is called
        # (ie Dummy.__... becomes Dummy. _TestCompoenent__...
        # instead of Dummy._Dummy__...). This is annoying but as this
        # attr should be internal only, we can deal with it here.

        self.assertEqual(0, len(Dummy._Dummy__flyweight_instances))

        first = Dummy(x=1, y=2)
        self.assertEqual(1, len(Dummy._Dummy__flyweight_instances))
        second = Dummy(x=1, y=2)
        self.assertEqual(1, len(Dummy._Dummy__flyweight_instances))
        self.assertIs(first, second)

        third = Dummy(x=3, y=2)
        self.assertEqual(2, len(Dummy._Dummy__flyweight_instances))
        self.assertIsNot(third, first)
        self.assertIsNot(third, second)

    def test_flyweight_components_are_immutable(self):

        class Dummy(Component):
            __flyweight__ = True
            x: int

        d = Dummy(44)
        self.assertRaises(AttributeError, setattr, d, 'x', 72)

    def test_flyweight_instances_are_not_shared(self):

        class Dummy1(Component):
            __flyweight__ = True
            x: int
            y: int

        class Dummy2(Component):
            __flyweight__ = True
            x: int
            y: int

        # No flyweight stugg was set on the base component class
        self.assertFalse(hasattr(Component, '_Component__flyweight_instances'))

        # Manled attribute created before any instanciation
        self.assertTrue(hasattr(Dummy1, '_Dummy1__flyweight_instances'))
        self.assertTrue(hasattr(Dummy2, '_Dummy2__flyweight_instances'))

        _ = Dummy1(x=1, y=2)
        _ = Dummy2(x=1, y=2)

        # Instance dicts set on their respective classes
        self.assertEqual(1, len(Dummy1._Dummy1__flyweight_instances))
        self.assertEqual(1, len(Dummy2._Dummy2__flyweight_instances))
        self.assertIsNot(
            Dummy1._Dummy1__flyweight_instances,
            Dummy2._Dummy2__flyweight_instances)

    def test_not_event_through_inheritance(self):
        """ Same as above, but webtwenn parent & child classes. """

        class Dummy1(Component):
            __flyweight__ = True
            x: int
            y: int

        class Dummy2(Dummy1):
            __flyweight__ = True
            z: int


        _ = Dummy1(x=1, y=2)
        _ = Dummy2(x=1, y=2, z=3)

        # Instance dicts set on their respective classes
        self.assertEqual(1, len(Dummy1._Dummy1__flyweight_instances))
        self.assertEqual(1, len(Dummy2._Dummy2__flyweight_instances))
        self.assertIsNot(
            Dummy1._Dummy1__flyweight_instances,
            Dummy2._Dummy2__flyweight_instances)

    @unittest.expectedFailure
    def test_flyweight_fails_with_dict_attr(self):
        """
        Can't hash dicts, so Components aith an dict attribute can't be
        flyweight for now. This may or may not be what we want in the long run, 
        but let's have a warning for now.
        """
        class Dummy(Component):
            __flyweight__ = True
            d: dict

        self.assertRaises(TypeError, Dummy, d={})

    def test_as_dict(self):

        class Dummy(Component):
            x: int
            y: int

        c = Dummy(x=1, y=2)
        self.assertEqual(c.as_dict(), {'x': 1, 'y': 2})

    def test_serialize_no_serialize(self):

        class Dummy(Component):
            __serialize__ = False
            x: int
            y: int

        c = Dummy(x=1, y=2)
        self.assertIsNone(c.serialize())

    def test_serialize_defaults_to_false(self):

        class Dummy(Component):
            x: int
            y: int

        c = Dummy(x=1, y=2)
        self.assertIsNone(c.serialize())

    def test_serialize_all(self):

        class Dummy(Component):
            __serialize__ = True
            x: int
            y: int

        c = Dummy(x=1, y=2)
        self.assertIsNotNone(c.serialize())
        self.assertEqual(c.serialize(), {'x': 1, 'y': 2})

    def test_serialize_listed_fields(self):

        class Dummy(Component):
            __serialize__ = ['x']
            x: int
            y: int

        c = Dummy(x=1, y=2)
        self.assertIsNotNone(c.serialize())
        self.assertEqual(c.serialize(), {'x': 1})
