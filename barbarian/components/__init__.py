from barbarian.utils.imports import init_package

__all__ = []


def init_components():
    for modname, mod in init_package(__file__, __name__):
        globals()[modname] = mod
        __all__.append(modname)
