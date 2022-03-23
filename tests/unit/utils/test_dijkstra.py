import unittest

from barbarian.utils.structures.dijkstra import DijkstraGrid


class DijsktraGridTest(unittest.TestCase):

    def _check_grid(self, grid, expected_array):
        for y, row in enumerate(expected_array):
            for x, c in enumerate(row):
                self.assertEqual(grid[x, y], c, f'Faling cell: ({x},{y})')

    def _print_grid(self, grid):
        # Used to check actual result while writing the tests.
        for x, y, c in grid:
            print(c, end = ' ')
            if x == grid.w - 1:
                print()

    def test_init(self):
        dg = DijkstraGrid(3, 3)
        self.assertTrue(all(c == dg.inf for c in dg.cells))

    def test_set_goal(self):
        dg = DijkstraGrid(3, 3)

        dg.set_goal(1, 1)
        self.assertEqual(dg[1, 1], 0)

        dg.set_goal(2, 2, 666)
        self.assertTrue(dg[2, 2], 666)

    def test_basic_compute(self):

        # Goal in the center
        dg = DijkstraGrid(5, 5)
        dg.set_goal(2, 2)
        dg.compute()

        expected = [
            [4, 3, 2, 3, 4],
            [3, 2, 1, 2, 3],
            [2, 1, 0, 1, 2],
            [3, 2, 1, 2, 3],
            [4, 3, 2, 3, 4],
        ]
        self._check_grid(dg, expected)

        # Goal in a corner
        dg = DijkstraGrid(5, 5)
        dg.set_goal(4, 4)
        dg.compute()

        expected = [
            [8, 7, 6, 5, 4],
            [7, 6, 5, 4, 3],
            [6, 5, 4, 3, 2],
            [5, 4, 3, 2, 1],
            [4, 3, 2, 1, 0],
        ]
        self._check_grid(dg, expected)

    def test_several_goals(self):

        dg = DijkstraGrid(5, 5)
        dg.set_goal(0, 0)
        dg.set_goal(4, 3)
        dg.compute()

        expected = [
            [0, 1, 2, 3, 3],
            [1, 2, 3, 3, 2],
            [2, 3, 3, 2, 1],
            [3, 3, 2, 1, 0],
            [4, 4, 3, 2, 1],
        ]
        self._check_grid(dg, expected)

    def test_basic_pedicate(self):

        dg = DijkstraGrid(3, 3)
        dg.set_goal(1, 1)
        dg.compute(
            # ignore first row
            predicate=lambda x, y, _: y != 0)

        expected = [
            [dg.inf, dg.inf, dg.inf],
            [1,      0,      1],
            [2,      1,      2],
        ]
        self._check_grid(dg, expected)

    def test_basic_cost_function(self):

        dg = DijkstraGrid(5, 5)
        dg.set_goal(2, 2)
        dg.compute(
            # Cell at (3, 2) (ie just east to the goal) costs 3
            cost_function=lambda x, y, _: 3 if (x, y) == (3, 2) else 1)

        expected = [
            [4, 3, 2, 3, 4],
            [3, 2, 1, 2, 3],
            [2, 1, 0, 3, 4],
            [3, 2, 1, 2, 3],
            [4, 3, 2, 3, 4],
        ]
        self._check_grid(dg, expected)
