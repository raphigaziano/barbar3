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
    # TODO: use dummy assets (same as above)
    ROOT_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'data'
    )

    def test_assets_explicit_path(self):
        """Check assets.get_path with an explicit path"""
        self.assertEqual(
            os.path.join(self.ROOT_PATH, 'terminal.png'),
            assets.get_path('terminal.png')
        )
        # TODO: nested paths

    def test_assets_ifragmented_path(self):
        """Check assets.get_path with an path fragments"""
        self.fail("TODO")
        # TODO: nested paths (not nested makes no sense here)

