import sys

from utils import settings

renderer = settings.RENDERER

__import__('renderers.%s' % renderer)
renderer = sys.modules['renderers.%s' % renderer]
