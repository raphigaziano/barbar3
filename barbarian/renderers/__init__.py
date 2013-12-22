import sys

from barbarian.gameio import settings

renderer = settings.RENDERER

__import__('barbarian.renderers.%s' % renderer)
renderer = sys.modules['barbarian.renderers.%s' % renderer]
