# -*- coding: utf8 -*-
"""
barbarian.map.py
================

Basic Map data structure.

"""

# Dummy map
from utils import settings, rng
MAP = [
    [rng.randint(0, 1) for i in range(settings.SCREEN_H)]
    for j in range(settings.SCREEN_W)
]
