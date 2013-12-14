# -*- coding: utf8 -*-
"""
barbarian.utils.assets.py
=========================

Define a few convenience function to load assets for the game.

"""
import os

ASSETS_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'assets'
)


def get_path(*args, **kwargs):
    """
    Return an absolute path to the requested asset file.

    Will consider the `data` irectory as the root for all files.

    args can be either a regular path (relative to the `data` directory),
    or a set of path fragments that will be joined together.

    """
    assets_root = kwargs.get('assets_root', ASSETS_ROOT)

    explicit_path = os.path.join(assets_root, args[0])
    if os.path.isfile(explicit_path):
        return explicit_path
    return os.path.join(assets_root, *args)
