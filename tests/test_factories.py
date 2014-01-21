# -*- coding: utf8 -*-
"""
Unit tests for the entity builders.

"""
import os
import unittest

from barbarian.io import data
from barbarian.objects import factories

from barbarian.objects.entity import Entity


class TestEntityDataReader(unittest.TestCase):

    def test_basic_data_retrieval(self):
        """ Simple retrieval of an entity's data. """
        d = {
            'foo': {
                'bar': 'baz'
            },
            'bar': {
                'baz': 'bar'
            }
        }
        self.assertEqual(d['foo'], factories._get_entity_data(d, 'foo'))
        self.assertEqual(d['bar'], factories._get_entity_data(d, 'bar'))

    def test_data_retrieval_with_commonmerge(self):
        """ Retrieved data includes the __common__ blocks. """
        d = {
            '__common__': {
                'foo': {
                    'baz': 'bar'
                }
            },
            'dummy': {
                'foo': {
                    'bar': 'baz'
                },
            },
        }
        r = factories._get_entity_data(d, 'dummy')
        self.assertIn('baz', r['foo'])
        self.assertEqual(d['__common__']['foo']['baz'], r['foo']['baz'])

    def test_data_retrieval_with_merge_and_override(self):
        """ Retrieved data ovverides the __common__ blocks if needed. """
        d = {
            '__common__': {
                'foo': {
                    'baz': 'bar'
                }
            },
            'dummy': {
                'foo': {
                    'bar': 'baz',
                    'baz': 'OVERRIDE',
                },
            },
        }
        r = factories._get_entity_data(d, 'dummy')
        self.assertIn('baz', r['foo'])
        self.assertEqual(d['dummy']['foo']['baz'], r['foo']['baz'])


class TestEntityBuilder(unittest.TestCase):

    def setUp(self):
        data.DATA_ROOT_PATH = os.path.join(
            os.path.dirname(__file__), 'dummy_data'
        )

    def test_simple_build(self):
        """ Building a simple entity from config file """
        e = factories.build_entity('rat', 12, 24)
        self.assertIsInstance(e, Entity)
        self.assertEqual(True, e.blocks)
        self.assertEqual('r', e.char)
