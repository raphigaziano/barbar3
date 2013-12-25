# -*- coding: utf8 -*-
"""
barbarian.mapgen.py

"""
from barbarian.map import Map
from barbarian.utils import rng

def make_map():
    def dummy_generator():
        """ Dummy map gen """
        return [
            rng.coin_flip() for i in range(80 * 40)
        ]

    return Map(80, 40, dummy_generator())


