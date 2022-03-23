"""
Misc data helpers.

"""
import copy


def merge_dicts(dst, src):
    """ Recursively merge src dictionnary into dst. """
    for k, v in src.items():
        if k not in dst:
            dst[k] = v
        if isinstance(v, dict):
            merge_dicts(dst[k], v)
    return dst


def make_hash(o):
    """
    Makes a hash from a dictionary, list, tuple or set to any level, that 
    contains only other hashable types (including any lists, tuples, sets, 
    and dictionaries).

    nicked from:

    https://stackoverflow.com/a/8714242
    """
    if isinstance(o, (set, tuple, list)):
        return tuple(make_hash(e) for e in o)
    if not isinstance(o, dict):
        return hash(o)

    new_o = copy.deepcopy(o)
    for k, v in new_o.items():
        new_o[k] = make_hash(v)

    return hash(tuple(frozenset(sorted(new_o.items()))))
