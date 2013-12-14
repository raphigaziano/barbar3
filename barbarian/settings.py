import os, sys

SETTINGS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'data', 'settings'
)

__MODULE__ = sys.modules[__name__]

with open(SETTINGS_PATH, 'r') as sf:
    for l in sf.readlines():
        if l.isspace() or l.startswith('#'):
            continue
        k, v = l.split('=')
        k, v = k.strip(), eval(v.strip())    # TODO: secure this
        setattr(__MODULE__, k, v)
