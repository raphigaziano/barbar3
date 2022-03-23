"""
Useful base data types.

"""
from enum import Enum


class StringAutoEnum(Enum):
    """ Enum keys defined with `auto()` will be set to KEY.lower(). """
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()


class FrozenDict(dict):
    """
    Basic immutable dictionnary.

    """

    def __init__(self, *args, **kwargs):
        self._hash = None
        super(FrozenDict, self).__init__(*args, **kwargs)

    def __hash__(self):
        if self._hash is None:
            hash_ = 0
            for pair in self.items():
                hash_ ^= hash(pair)
            self._hash = hash_
        return self._hash

    def _immutable(self, *args, **kws):
        raise TypeError('cannot change object - object is immutable')

    # makes (deep)copy alot more efficient
    def __copy__(self):
        return self

    def __deepcopy__(self, memo=None):
        if memo is not None:
            memo[id(self)] = self
        return self

    __setitem__ = _immutable
    __delitem__ = _immutable
    pop = _immutable
    popitem = _immutable
    clear = _immutable
    update = _immutable
    setdefault = _immutable
