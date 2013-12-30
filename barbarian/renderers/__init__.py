# -*- coding: utf8 -*-
"""
barbarian.renderers
===================

Rendering root.

Expose the active renderer object/module to the rest of the game.

"""
import sys

from barbarian.io import settings

renderer = settings.RENDERER

__import__('barbarian.renderers.%s' % renderer)
renderer = sys.modules['barbarian.renderers.%s' % renderer]
