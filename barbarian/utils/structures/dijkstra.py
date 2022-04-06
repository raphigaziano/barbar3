"""
Dijkstra implementation.

"""
import sys
import heapq
import logging

from barbarian.utils.structures.grid import Grid


logger = logging.getLogger(__name__)


class DijkstraGrid(Grid):
    """
    Specialized grid implementing Dijsktra's algorithm.

    Inspired by the famous article:
    http://roguebasin.com/?title=The_Incredible_Power_of_Dijkstra_Maps

    See also:
    http://www.roguebasin.com/index.php/Dijkstra_Maps_Visualized

    """
    inf = sys.maxsize

    def __init__(self, width, height):
        super().__init__(width, height, [self.inf] * (width * height))
        self.goals = set()

    def set_goal(self, x, y, weight=0):
        """ Add a potential destination at position (x, y). """
        idx = self._cartesian_to_idx(x, y)
        self.cells[idx] = weight
        self.goals.add((weight, idx))

    def compute(self, predicate=None, cost_function=None):
        """ Update the map with distances to its goal cells. """

        predicate = predicate or (lambda _, __, ___: True)
        cost_function = cost_function or (lambda _, __, ___: 1)

        visited = {i: False for i in range(self.w * self.h)}
        pqueue = [(0, idx) for _, idx in self.goals]
        while pqueue:
            _, c_idx = heapq.heappop(pqueue)
            curval = self.cells[c_idx]

            if visited[c_idx]:
                continue
            visited[c_idx] = True

            cx, cy = c_idx % self.w, c_idx // self.w

            for nx, ny in (
                    (cx, cy - 1),       # N
                    (cx + 1, cy),       # E
                    (cx, cy + 1),       # S
                    (cx - 1, cy),       # W
                    (cx - 1, cy - 1),   # NW
                    (cx + 1, cy - 1),   # NE
                    (cx - 1, cy + 1),   # SW
                    (cx + 1, cy + 1),   # SE
            ):
                if not (0 <= nx < self.w and 0 <= ny < self.h):
                    continue
                n_idx = nx + (ny * self.w)
                n = self.cells[n_idx]
                if not predicate(nx, ny, n):
                    continue
                cost = cost_function(nx, ny, n)
                if (curval + cost) < n:
                    self.cells[n_idx] = curval + cost
                    heapq.heappush(pqueue, (curval + cost, n_idx))

    @classmethod
    def new(cls, width, height, *goals, predicate=None, cost_function=None):
        """
        Shortcut to nitialize a dtra map, set its goal cells and
        compute pathes all in one go.

        """
        dg = cls(width, height)
        for g in goals:
            weight = 0
            try:
                weight, gx, gy = g
            except ValueError:
                gx, gy = g
            dg.set_goal(gx, gy, weight)
        dg.compute(predicate, cost_function)
        return dg
