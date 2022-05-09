import os, sys
import timeit

# This assumes we're running from the <root>/bin folder
root_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, root_dir)

from barbarian.game import Game

g = Game()
# g.MAP_DEBUG = True
g.init_game()
g.start_game(seed='1628088563624636737')
# g.start_game(seed=None)

print('Map cells sum:', sum(ord(c.value) for c in g.current_level.map.cells))

if __name__ == '__main__':
    timer = timeit.Timer('g.state.update(g)',  globals=globals())
    try:
        print(timer.repeat(5, 100))
    except:
        timer.print_exc()

