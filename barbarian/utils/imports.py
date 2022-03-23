""" Import helpers. """
import os
from importlib import import_module


def init_package(calling_file, calling_name):
    """
    Dynamcally import all submodules from a package.

    Should be calling from the package's __init__.py,
    with __file__ and __name__ as arguments.

    """
    mod_dir = os.path.dirname(os.path.abspath(calling_file))
    # get all python files
    for filename in os.listdir(mod_dir):
        if os.path.isfile(os.path.join(mod_dir, filename)):
            fn, ext = os.path.splitext(filename)
            if fn == '__init__':
                continue
            if ext == '.py':
                modname = '.'.join((calling_name, fn))
                yield fn, import_module(modname)
