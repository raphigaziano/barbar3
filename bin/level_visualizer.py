#! /usr/bin/env python
import sys, os
import curses
# TODO: Aloow specification of the game import path through cmd opt.
barbar_dir = os.path.abspath(
    (os.path.dirname(os.path.dirname(__file__))))
print('Import path: %s' % barbar_dir)
sys.path.append(barbar_dir)


import random

from barbarian.utils.rng import Rng
from barbarian.genmap import builders


MAX_X, MAX_Y = None, None

def init_curses():
    global MAX_X, MAX_Y

    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    screen.keypad(1)
    # screen.timeout(0)         ?

    curses.start_color()
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    MAX_Y, MAX_X = screen.getmaxyx()

    return screen

def shut_down_curses(screen):
    curses.nocbreak()
    # screen.timeout(-1)        ?
    screen.keypad(0)
    curses.curs_set(1)
    curses.echo()
    curses.endwin()


def draw(screen, dmap):
    screen.clear()
    for x, y, cell in dmap:
        # Trying to draw outside the terminal bounds causes a crash
        if x >= MAX_X -1 or y >= MAX_Y -1:
            continue
        char = cell.value
        screen.addch(y, x, char, curses.color_pair(0))


builders = {
    'simple': builders.SimpleMapBuilder,
    'bsp': builders.BSPMapBuilder,
    'bsp_interior': builders.BSPInteriorMapBuilder,
    'cellular': builders.CellularAutomataMapBuilder,
}

def build_map(rng, builder):
    if builder == 'any':
        builder = rng.choice(list(builders.values()))()
    else:
        builder = builders[builder]()
    m =  builder.build_map(MAX_X, MAX_Y-1, 1)
    return m


def main(builder, seed):

    Rng.add_rng('dungeon', seed)
    screen = init_curses()

    dmap = build_map(Rng.dungeon, builder)
    draw(screen, dmap)

    try:
        while True:

            c = screen.getch()

            if c == ord('q'):
                return 'quit'
            else:
                dmap = build_map(Rng.dungeon, builder)
                draw(screen, dmap)
    finally:
        shut_down_curses(screen)

    return 0


if __name__ == '__main__':
    builder = sys.argv[1]
    try: 
        seed = sys.argv[2]
    except IndexError:
        seed = None
    sys.exit(main(builder, seed))
