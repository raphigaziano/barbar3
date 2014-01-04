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


class TestBaseEntityAttributeAccess(unittest.TestCase):

    class FooComponent(object):
        def __init__(self):
            self.foo = 'foo'

    class BarComponent(object):
        def __init__(self):
            self.bar = 'bar'

    class FooBarComponent(object):
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

    def test_simple_attribute_access(self):
        """ Accessing contained components attrs from the entity """
        self.assertEqual('foo', self.e.foo)
        self.assertEqual('bar', self.e.bar)

    def test_missing_attribute_access(self):
        """ Accessing a non-existent entity attribute should return a NullProp """
        self.assertIsInstance(self.e.moop, entity.NullProperty)

    def test_missing_method_access(self):
        """ Caling a non-existent entity method should return a NullProp """
        self.assertIsInstance(self.e.moop(), entity.NullProperty)

    def test_component_override(self):
        """ Pushing component to the front to override some attrs or methods """
        self.e.push_component(self.FooBarComponent())
        self.assertEqual('bar', self.e.foo)
        self.e.pop_component()
        self.assertEqual('foo', self.e.foo)

class TestNullProperty(unittest.TestCase):

    def setUp(self):
        self.null_prop = entity.NullProperty()

    def test_getattr(self):
        """ Accessing a NullProperty attribute should return another NullProperty """
        self.assertIsInstance(self.null_prop.foo, entity.NullProperty)
        self.assertIsInstance(self.null_prop.bar, entity.NullProperty)

    def test_call(self):
        """ Calling a NullProperty instance should return another NullProperty """
        self.assertIsInstance(self.null_prop(), entity.NullProperty)

    def test_is(self):
        """ is test with a NullProperty returns based on the class:
            Two NullProperty instances are considered equal """
        null_prop = entity.NullProperty()
        self.assertTrue(null_prop == self.null_prop)
        other_prop = object()
        self.assertFalse(other_prop == self.null_prop)

