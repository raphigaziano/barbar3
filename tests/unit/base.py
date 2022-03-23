"""
Common utils for unit tests.

"""
from contextlib import contextmanager

import barbarian.raws


class DummyRawsMixin:

    _dummy_raws = {}

    @property
    def dummy_raws(self):
        return self._dummy_raws.copy()

    @contextmanager
    def patch_raws(self, var_name):
        original = getattr(barbarian.raws, var_name)
        patched_raws = self.dummy_raws.copy()
        setattr(barbarian.raws, var_name, patched_raws)
        yield patched_raws
        setattr(barbarian.raws, var_name, original)
