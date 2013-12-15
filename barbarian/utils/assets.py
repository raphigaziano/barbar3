# -*- coding: utf8 -*-
"""
barbarian.utils.assets.py
=========================

Define a few convenience function to load assets for the game.

"""
import os

from utils.settings import ASSETS_ROOT, RENDERER

ASSETS_ROOT = os.path.join(ASSETS_ROOT, RENDERER)

def get_path(*args, **kwargs):
    """
    Return an absolute path to the requested asset file.

    Will consider the `assets` directory as the root for all files.

    args can be either a regular path (relative to the `data` directory),
    or a set of path fragments that will be joined together.

    An optional `assets_root` keyword argument can override the default
    root directory.

    """
    assets_root = kwargs.get('assets_root', ASSETS_ROOT)

    explicit_path = os.path.join(assets_root, args[0])
    if os.path.isfile(explicit_path):
        return explicit_path
    return os.path.join(assets_root, *args)
