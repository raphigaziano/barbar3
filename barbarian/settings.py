"""
Game settings.

This is just a constants file for now, but we should add
logic to load and handle config from data files.

"""
DEBUG = False
MAP_DEBUG = False
MAP_W = 80
MAP_H = 50

LOGCONFIG = {
    'version': 1,
    'formatters': {
        'simple': {
            'format': '%(name)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'stream': 'ext://sys.stderr',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'barbarian': {
            'level': 'INFO',
            'handlers': ['console'],
        },
        'barbarian.events': {
            'level': 'INFO',
        },
    },
}

RAWS_ROOT = 'raws'

MAX_SPAWNS = 4  # per zone
