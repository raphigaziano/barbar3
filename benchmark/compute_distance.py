import os, sys
import timeit

# This assumes we're running from the <root>/bin folder
root_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, root_dir)

from barbarian.game import Game
from barbarian.pathfinding import get_path_map


g = Game()
# g.MAP_DEBUG = True
g.init_game()
g.start_game(seed='4501749665504327068')

print('Map cells sum:', sum(ord(c.value) for c in g.current_level.map.cells))
print('num open cells:', len([
    c for c in g.current_level.map.cells
    if c in g.current_level.map.BLOCKING_TILE_TYPES]))
print('num actors', len(g.current_level.actors))
print('num props', len(g.current_level.props))

def compute_dist_map():
    level = g.current_level

    get_path_map(
        level, (g.player.pos.x, g.player.pos.y),
        # predicate=lambda x, y, _: not level.map.cell_blocks(x, y)
        predicate=lambda x, y, _: not level.is_blocked(x, y)
    )


if __name__ == '__main__':
    timer = timeit.Timer('compute_dist_map()',  globals=globals())
    try:
        print(timer.repeat(5, 100))
    except:
        timer.print_exc()

