import os
import unittest
from unittest.mock import patch, mock_open
from contextlib import contextmanager

from tests.unit.base import DummyRawsMixin

from barbarian.settings import RAWS_ROOT
from barbarian.raws import get_spawn_data, get_entity_data


class TestEntityRaws(DummyRawsMixin, unittest.TestCase):

    _dummy_raws = {
        'actors': {
            'actor_1': {
                'foo_component': {'foo': 'oof'},
            },
            'actor_2': {
                'bar_component': {'bar': 'rab'},
            },
        },
        'props': {},
        'items': {
            'parent_item': {
                'base_component': {'moop': 'meep'},
                'partial_component': {'foo': 'oof'},
                'overriden_component': {'x': 0, 'y': 0},
            },
            'child_item': {
                '_parent': 'parent_item',
                'partial_component': {'bar': 'rab'},
                'overriden_component': {'x': 42},
            },
        },
        'spawn': ['lol', 'wut'],
    }

    def test_get_entity_data(self):
        with self.patch_raws('_entity_tables'):
            ed = get_entity_data('actor_1', 'actors')
            self.assertDictEqual({'foo_component': {'foo': 'oof'}}, ed)
            ed = get_entity_data('actor_2', 'actors')
            self.assertDictEqual({'bar_component': {'bar': 'rab'}}, ed)

    def test_load_table_from_disk(self):

        with self.patch_raws('_entity_tables'):

            with patch(
                'builtins.open',
                mock_open(read_data='prop_1:\n  foo: bar')
            ) as m_open:

                # Table already defined: no file reading
                get_entity_data('actor_1', 'actors')
                m_open.assert_not_called()

                # Table not defined: grab it from disk
                ed = get_entity_data('prop_1', 'props')
                # One call per table
                self.assertEqual(4, m_open.call_count)
                # Check all raws pathes are read, each prefixed with
                # RAWS_ROOT
                for path in (
                    os.path.join(RAWS_ROOT, 'entities/actors.yaml'),
                    os.path.join(RAWS_ROOT, 'entities/props.yaml'),
                    os.path.join(RAWS_ROOT, 'entities/items.yaml'),
                    os.path.join(RAWS_ROOT, 'entities/spawn.yaml'),
                ):
                    m_open.assert_any_call(path, 'r', encoding='utf-8')

                self.assertDictEqual({'foo': 'bar'}, ed)

                # Do not read again for the tables we just loaded
                m_open.reset_mock()
                ed = get_entity_data('prop_1', 'props')
                m_open.assert_not_called()
                self.assertDictEqual({'foo': 'bar'}, ed)

    def test_invalid_table(self):
        with self.patch_raws('_entity_tables'):
            with self.assertLogs('barbarian.raws', 'WARNING'):
                get_entity_data('wat', 'woot')

    def test_invalid_entity_name(self):
        # Should emit a warning, but leave it to the caller
        # to avoid spamming the logs (Tested in test_spawn). 
        # This means a simple no-op here.
        ed = get_entity_data('gojohnnygo', 'actors')
        self.assertIsNone(ed)

    def test_entity_inheritance(self):
        with self.patch_raws('_entity_tables'):
            ed = get_entity_data('child_item', 'items')
            self.assertDictEqual({
                    'base_component': {'moop': 'meep'},
                    'partial_component': {'foo': 'oof', 'bar': 'rab'},
                    'overriden_component': {'x': 42, 'y': 0},
                }, ed)

    def test_get_spawn_data(self):
        with self.patch_raws('_entity_tables'):
            sd = get_spawn_data()
            self.assertListEqual(['lol', 'wut'], sd)

    def test_load_spawn_data_from_disk(self):

        with self.patch_raws('_entity_tables') as patched_raws:

            with patch(
                'builtins.open',
                mock_open(read_data="['cat', 'dog']")
            ) as m_open:

                # Table already defined: no file reading
                get_spawn_data()
                m_open.assert_not_called()

                # Table not defined: grab it from disk
                patched_raws['spawn'] = []
                sd = get_spawn_data()
                # All tables are loaded, just like loadind entity data
                self.assertEqual(4, m_open.call_count)
                # Check all raws pathes are read, each prefixed with
                # RAWS_ROOT
                for path in (
                    os.path.join(RAWS_ROOT, 'entities/actors.yaml'),
                    os.path.join(RAWS_ROOT, 'entities/props.yaml'),
                    os.path.join(RAWS_ROOT, 'entities/items.yaml'),
                    os.path.join(RAWS_ROOT, 'entities/spawn.yaml'),
                ):
                    m_open.assert_any_call(path, 'r', encoding='utf-8')

                self.assertListEqual(['cat', 'dog'], sd)

                # Do not read again for the tables we just loaded
                m_open.reset_mock()
                sd = get_spawn_data()
                m_open.assert_not_called()
                self.assertListEqual(['cat', 'dog'], sd)
