import sys

from gameio import settings

renderer = settings.RENDERER

__import__('renderers.%s' % renderer)
renderer = sys.modules['renderers.%s' % renderer]
