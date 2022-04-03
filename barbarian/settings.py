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
DISABLE_SPAWNING = False

DEFAULT_REGEN_RATE = 10
DEFAULT_REGEN_AMOUNT = 1

DEFAULT_HUNGER_RATE = 5
MAX_HUNGER_SATIATION = 120
HUNGER_DMG_CHANCE = 30
HUNGER_DMG = '1d2'

HUNGER_STATES = (
    # (State name, threshold)
    ('starving',     (MAX_HUNGER_SATIATION // 3) // 2),
    ('very hungry',  MAX_HUNGER_SATIATION // 3),
    ('hungry',       (MAX_HUNGER_SATIATION // 3) * 2),
    ('satiated',     MAX_HUNGER_SATIATION - ((MAX_HUNGER_SATIATION // 5) // 2)),
)

NO_REGEN_HUNGER_STATES = ('very hungry', 'starving')
