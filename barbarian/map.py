# -*- coding: utf8 -*-
"""
barbarian.map.py
================

Basic Map data structure.

"""


def dummy_generator():
    from utils import rng
    return [
        rng.coin_flip() for i in range(80 * 40)
    ]


class OutOfBoundMapError(IndexError, Exception):
    pass

class Map(object):

    """ Basic Map object """

    def __init__(self, width, height, generator):
        # Placeholders w & h
        self.w = width
        self.h = height
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
            x, y = self._idx_to_cartesian(i)
            yield x, y, c
        raise StopIteration

    def slice(self, x, y, w, h):
        cells = [0, 0, 0]
        return self.__class__(w, h, lambda: cells)

    ### Internal Utils ###
    ######################

    def _idx_to_cartesian(self, idx):
        return idx % self.w, idx / self.w

    def _cartesian_to_idx(self, x, y):
        return x + (y * self.w)

