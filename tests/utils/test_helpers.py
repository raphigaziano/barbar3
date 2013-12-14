#! /usr/bin/env python
#-*- coding:utf-8 -*-
"""Unit tests for the various helpers functions (settings & assets management)"""
import os
import unittest

from utils import settings
from utils import assets


class TestSettings(unittest.TestCase):
    # TODO: use a dummy setting file to avoid hardcoding test values
    # TODO: check more types
    def test_settings(self):
        """Assert settings loaded correctly"""
        self.assertTrue(hasattr(settings, 'SCREEN_W'))
        self.assertEqual(80, settings.SCREEN_W)
        self.assertEqual(int, type(settings.SCREEN_W))


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


