#! /usr/bin/env python
#-*- coding:utf-8 -*-
"""Unit tests for the various helpers functions (settings & assets management)"""
import os
import unittest
from io import StringIO

from barbarian.io import settings
from barbarian.io import assets
from barbarian.io import data


class TestSettings(unittest.TestCase):

    SETTING_FILE = os.path.join(
        os.path.dirname(__file__), 'dummy_settings', 'settings'
    )

    def setUp(self):
        self.clear_settings()

    def clear_settings(self):
        settings._SETTINGS_DICT = {}

    def get_setting(self, *args, **kwargs):
        """
        Mock for settings._get_setting.

        Simply set the `settings_file` argument to the dummy settings file.

        """
        return settings._get_setting(
            settings_file=self.SETTING_FILE, *args, **kwargs
        )

    def test_get_setting(self):
        """ Testing simple setting retrieval """
        self.assertEqual('foo', self.get_setting('STR'))
        self.assertEqual(666, self.get_setting('INT'))

    def test_missing_setting(self):
        """ Missing (but not required) setting should default to None. """
        self.assertEqual(None, self.get_setting('MISSING_SETTING'))

    def test_missing_required_setting(self):
        """ Missing and required setting should raise an exception. """
        self.assertRaises(
            settings.InvalidSetting,
            self.get_setting,
            ('MISSING_SETTING',),
            required=True
        )

    def test_missing_default_setting(self):
        """ Missing setting should default to its default value if specified. """
        self.assertEqual(
            'FOO', self.get_setting('MISSING_SETTING', default='FOO')
        )
        self.clear_settings()
        self.assertEqual(
            666, self.get_setting('MISSING_SETTING', default=666)
        )

    def test_invalid_type(self):
        """ Invalidly typed settings should raise an exception. """
        self.assertRaises(
            settings.InvalidSetting, self.get_setting,
            ('STR',), py_type=int
        )
        self.assertRaises(
            settings.InvalidSetting, self.get_setting,
            ('INT',), py_type=str
        )

class TestAssets(unittest.TestCase):

    TEST_ASSETS_ROOT = os.path.join(os.path.dirname(__file__), 'dummy_assets')

    def get_path(self, *args):
        """
        Mock for assets.get_path.

        Simply set the `assets_root` argument to the test assets directory.

        """
        return assets.get_path( *args, assets_root=self.TEST_ASSETS_ROOT)

    def test_assets_explicit_path(self):
        """Check assets.get_path with an explicit path"""
        path = os.path.join(self.TEST_ASSETS_ROOT, 'dummy')
        self.assertEqual(path, self.get_path('dummy'))
        self.assertTrue(os.path.exists(self.get_path(path)))

        path = os.path.join(self.TEST_ASSETS_ROOT, 'libtcod/fonts/terminal.png')
        self.assertEqual(path, self.get_path(path))
        self.assertTrue(os.path.exists(self.get_path(path)))

    def test_assets_fragmented_path(self):
        """Check assets.get_path with an path fragments"""
        path = os.path.join(self.TEST_ASSETS_ROOT, 'libtcod/fonts/terminal.png')
        args = ('libtcod', 'fonts', 'terminal.png')
        self.assertEqual(path, self.get_path(*args))
        self.assertTrue(os.path.exists(self.get_path(*args)))

class TestDataReaders(unittest.TestCase):

    def test_double_quotes_convertion(self):
        """Convert single quotes in json fiels to double quotes to keep parser from blowing up """
        f = StringIO(u"{'foo': 'bar'}")
        self.assertEqual({'foo': 'bar'}, data.read_data(f))
