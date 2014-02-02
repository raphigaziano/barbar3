#-*- coding:utf-8 -*-
""" Unit tests for the base Entity class. """
import unittest
from mock import Mock

from barbarian.objects import entity

class TestBaseEntityComponentManagement(unittest.TestCase):

    def setUp(self):
        self.e = entity.Entity()
        self.mock_comp_1, self.mock_comp_2, self.mock_comp_3 =\
                Mock(), Mock(), Mock()

    def test_add_component(self):
        """ Add unindexed component """
        self.e.add_component(self.mock_comp_1)
        self.assertEqual(1, len(self.e._components))
        self.assertListEqual([self.mock_comp_1], self.e._components)
        self.e.add_component(self.mock_comp_2)
        self.assertEqual(2, len(self.e._components))
        self.assertListEqual(
            [self.mock_comp_1, self.mock_comp_2], self.e._components
        )

    def test_add_indexed_component(self):
        """ Add a component with an explicit index """
        self.e.add_component(self.mock_comp_1)
        self.e.add_component(self.mock_comp_2, 0)
        self.assertListEqual(
            [self.mock_comp_2, self.mock_comp_1], self.e._components
        )
        self.e.add_component(self.mock_comp_3, 1)
        self.assertListEqual(
            [self.mock_comp_2, self.mock_comp_3, self.mock_comp_1],
            self.e._components
        )

    def test_push_component(self):
        """ Push a component at the front of the componenet list """
        self.e.push_component(self.mock_comp_1)
        self.e.push_component(self.mock_comp_2)
        self.assertListEqual(
            [self.mock_comp_2, self.mock_comp_1], self.e._components
        )
        self.e.push_component(self.mock_comp_3)
        self.assertListEqual(
            [self.mock_comp_3, self.mock_comp_2, self.mock_comp_1],
            self.e._components
        )

    def test_pop_component(self):
        """ Pop a component off the front of the list """
        self.e.push_component(self.mock_comp_1)
        self.e.push_component(self.mock_comp_2)
        self.e.push_component(self.mock_comp_3)

        self.assertEqual(self.mock_comp_3, self.e.pop_component())
        self.assertEqual(self.mock_comp_2, self.e.pop_component())
        self.assertEqual(self.mock_comp_1, self.e.pop_component())

        self.assertListEqual([], self.e._components)

    def test_update_component(self):
        """ Updating Entity also updates all updatable components. """
        no_update_comp = Mock(spec=object)

        self.e.push_component(self.mock_comp_1)
        self.e.push_component(no_update_comp)
        self.e.push_component(self.mock_comp_3)

        self.e.update()

        self.mock_comp_1.update.assert_called_once_with()
        self.mock_comp_3.update.assert_called_once_with()

        self.assertFalse(no_update_comp.called)

class TestBaseEntityComponentsAccess(unittest.TestCase):

    class FooComponent(entity.components.BaseComponent):
        def __init__(self):
            self.foo = 'foo'

    class BarComponent(entity.components.BaseComponent):
        def __init__(self):
            self.bar = 'bar'

    class FooBarComponent(entity.components.BaseComponent):
        def __init__(self):
            self.foo = 'bar'

    def setUp(self):
        self.e = entity.Entity()
        # self.foo_component, self.bar_component = Mock(), Mock()
        # self.foo_component.foo.return_value = 'foo'
        # self.bar_component.bar.return_value = 'bar'
        self.foo_component = self.FooComponent()
        self.bar_component = self.BarComponent()

        self.e.add_component(self.foo_component)
        self.e.add_component(self.bar_component)

    def test_has_component(self):
        """ Component presence assertion """
        self.assertTrue(self.e.has_component(self.FooComponent))
        self.assertFalse(self.e.has_component(self.FooBarComponent))

    def test_has_component_subclass(self):
        """ Component presence assertion, checking for a base component class """
        self.assertTrue(self.e.has_component(entity.components.BaseComponent))

    def test_filter_by_components_string_lookup(self):
        """ Component presence assertion, string lookup """
        self.assertTrue(self.e.has_component('FooComponent'))
        self.assertTrue(self.e.has_component('BarComponent'))

    def test_has_property(self):
        """ Entity property check """
        self.assertTrue(self.e.has_property('foo'))
        self.assertTrue(self.e.has_property('bar'))
        self.assertFalse(self.e.has_property('moop'))

    def test_set_property(self):
        """ Set a property on a component """
        self.e.set_property('foo', 'bar')
        self.assertFalse('foo' in self.e.__dict__)
        self.assertEqual('bar', self.foo_component.foo)

        self.e.set_property('bar', 'foo')
        self.assertFalse('bar' in self.e.__dict__)
        self.assertEqual('foo', self.bar_component.bar)

    def test_set_property_current_component(self):
        """ Set property on the active (top of the stack) component only """
        self.e.add_component(self.FooComponent())
        self.e.set_property('foo', 'bar')
        self.assertEqual('bar', self.foo_component.foo)
        self.assertNotEqual('bar', self.e._components[-1].foo)

    def test_get_property(self):
        """ Property retrieval via get method """
        self.assertEqual('foo', self.e.get('foo'))
        self.assertEqual('bar', self.e.get('bar'))
        self.assertEqual(self.e.NULL_PROPERTY, self.e.get('moop'))

    def test_get_property_with_default(self):
        """ Property retrieval via get mehod with default value """
        self.assertEqual('moop', self.e.get('moop', default='moop'))

    def test_simple_attribute_access(self):
        """ Accessing contained components attrs from the entity """
        self.assertEqual('foo', self.e.foo)
        self.assertEqual('bar', self.e.bar)

    def test_missing_attribute_access(self):
        """ Accessing a non-existent entity attribute should return a NullProp """
        self.assertIsInstance(self.e.moop, entity.NullProperty)

    def test_missing_method_access(self):
        """ Caling a non-existent entity method should return a NullProp """
        self.assertTrue(self.e.moop is self.e.NULL_PROPERTY)

    # def test_missing_method_access(self):
    #     """ Caling a non-existent entity method should return a NullProp """
    #     self.assertIsInstance(self.e.moop(), entity.NullProperty)

    def test_component_override(self):
        """ Pushing component to the front to override some attrs or methods """
        self.e.push_component(self.FooBarComponent())
        self.assertEqual('bar', self.e.foo)
        self.e.pop_component()
        self.assertEqual('foo', self.e.foo)

class TestEntityContainer(unittest.TestCase):

    class FooComponent(entity.components.BaseComponent):
        def __init__(self):
            self.foo = 'foo'

    class BarComponent(entity.components.BaseComponent):
        def __init__(self):
            self.bar = 'bar'

    class FooBarComponent(entity.components.BaseComponent):
        def __init__(self):
            self.foo = 'bar'

    def setUp(self):
        self.container = entity.EntityContainer()

        self.foo_entity = entity.Entity()
        self.foo_entity.add_component(self.FooComponent())
        self.bar_entity = entity.Entity()
        self.bar_entity.add_component(self.BarComponent())
        self.foobar_entity = entity.Entity()
        self.foobar_entity.add_component(self.FooBarComponent())

        self.container.append(self.foo_entity)
        self.container.append(self.bar_entity)

    def test_filter_by_component(self):
        """ Get all entities containing a given component """
        foo_comps = [c for c in
            self.container.filter_by_components(self.FooComponent)
        ]
        bar_comps = [c for c in
            self.container.filter_by_components(self.BarComponent)
        ]
        foobar_comps = [c for c in
            self.container.filter_by_components(self.FooBarComponent)
        ]

        self.assertEqual(1, len(foo_comps))
        self.assertEqual(1, len(bar_comps))
        self.assertEqual(0, len(foobar_comps))

        for e in foo_comps:
            self.assertTrue(e.has_component(self.FooComponent))
        for e in bar_comps:
            self.assertTrue(e.has_component(self.BarComponent))

    def test_filter_by_components(self):
        """ Filter entities by components, passing several component types """
        foo_and_bar_entity = entity.Entity()
        foo_and_bar_entity.add_component(self.FooComponent())
        foo_and_bar_entity.add_component(self.BarComponent())
        self.container.append(foo_and_bar_entity)

        foo_and_bar_comps = [c for c in
            self.container.filter_by_components(
                self.FooComponent, self.BarComponent
            )
        ]
        self.assertEqual(1, len(foo_and_bar_comps))
        for e in foo_and_bar_comps:
            self.assertTrue(e.has_component(self.FooComponent))
            self.assertTrue(e.has_component(self.BarComponent))

    def test_filter_by_property(self):
        """ Get all entities possessing the given property """
        foo_props = [c for c in
            self.container.filter_by_property('foo')
        ]
        bar_props = [c for c in
            self.container.filter_by_property('bar')
        ]
        foobar_props= [c for c in
            self.container.filter_by_property('foobar')
        ]

        self.assertEqual(1, len(foo_props))
        self.assertEqual(1, len(bar_props))
        self.assertEqual(0, len(foobar_props))

        for e in foo_props:
            self.assertTrue(e.has_property('foo'))
        for e in bar_props:
            self.assertTrue(e.has_property('bar'))

    def test_filter_by_property_with_explicit_val(self):
        """ Get all entities with a given property set at the given value """
        ok_props = [c for c in
            self.container.filter_by_property('foo', 'foo')
        ]
        nok_props = [c for c in
            self.container.filter_by_property('foo', 'bar')
        ]

        self.assertEqual(1, len(ok_props))
        self.assertEqual(0, len(nok_props))

        for e in ok_props:
            self.assertEqual('foo', e.foo)

