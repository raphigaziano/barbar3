# -*- coding: utf8 -*-
"""
barbarian.map.py
================

Basic Map data structure.

"""

from utils import settings, rng


def dummy_generator():
    return [
        rng.coin_flip() for i in range(settings.MAP_W * settings.MAP_H)
    ]


class OutOfBoundMapError(IndexError, Exception):
    pass

class Map(object):

    """ Basic Map object """

    def __init__(self, generator):
        # Dummy map gen
        self.cells = generator()

    def get_cell(self, x, y):
        try:
            return self.cells[self._cartesian_to_idx(x, y)]
        except IndexError:
            raise OutOfBoundMapError(
                "Can't access cell %d-%d: Out of bounds" % (x, y)
            )

    def __iter__(self):
        for i, c in enumerate(self.cells):
            yield self._idx_to_cartesian(i), c
        raise StopIteration

    ### Internal Utils ###
    ######################

    def _idx_to_cartesian(self, idx):
        return idx / settings.MAP_H, idx % settings.MAP_H

    def _cartesian_to_idx(self, x, y):
        # WRONG
        return x+y

