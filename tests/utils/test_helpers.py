#! /usr/bin/env python
#-*- coding:utf-8 -*-
"""Unit tests for the various helpers functions (settings & assets management)"""
import os
import unittest

from utils import settings
from utils import assets


class TestSettings(unittest.TestCase):

    def setUp(self):
        self.clear_settings()

    def clear_settings(self):
        settings._SETTINGS_DICT = {}

    # TODO: use a dummy setting file to avoid hardcoding test values
    # TODO: check more types
    def test_settings(self):
        """Assert settings loaded correctly"""
        self.assertTrue(hasattr(settings, 'SCREEN_W'))
        self.assertEqual(80, settings.SCREEN_W)
        self.assertEqual(int, type(settings.SCREEN_W))

    def test_missing_setting(self):
        """ Missing (but not required) setting should default to None. """
        self.assertEqual(None, settings._get_setting('MISSING_SETTING'))

    def test_missing_required_setting(self):
        """ Missing and required setting should raise an exception. """
        self.assertRaises(
            settings.InvalidSetting,
            settings._get_setting,
            ('MISSING_SETTING'),
            required=True
        )

    def test_missing_default_setting(self):
        """ Missing setting should default to its default value if specified. """
        self.assertEqual(
            'FOO', settings._get_setting('MISSING_SETTING', default='FOO')
        )
        self.clear_settings()
        self.assertEqual(
            666, settings._get_setting('MISSING_SETTING', default=666)
        )

class TestAssets(unittest.TestCase):

    def setUp(self):
        assets.ROOT_DIR = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'dummy_assets'
        )

    def test_assets_explicit_path(self):
        """Check assets.get_path with an explicit path"""
        path = os.path.join(assets.ROOT_DIR, 'dummy')
        self.assertEqual(path, assets.get_path('dummy'))
        self.assertTrue(os.path.exists(assets.get_path(path)))

        path = os.path.join(assets.ROOT_DIR, 'libtcod/fonts/terminal.png')
        self.assertEqual(path, assets.get_path(path))
        self.assertTrue(os.path.exists(assets.get_path(path)))

    def test_assets_ifragmented_path(self):
        """Check assets.get_path with an path fragments"""
        path = os.path.join(assets.ROOT_DIR, 'libtcod/fonts/terminal.png')
        args = ('libtcod', 'fonts', 'terminal.png')
        self.assertEqual(path, assets.get_path(*args))
        self.assertTrue(os.path.exists(assets.get_path(*args)))


