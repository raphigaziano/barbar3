"""
Pathfinding routines.

"""
from barbarian.utils.structures.dijkstra import DijkstraGrid
from barbarian.utils.geometry import vector_to


def get_path_map(level, start_pos, *goals, predicate=None, cost_function=None):
    """
    Compute a dijtra path map centered on `start_pos`.

    All arguments except `level` will be passed to `DiskstraGrid.new`,
    see that class's docs for more info.

    """
    # Default predicate excludes cells occupied by a prop or an actor.
    # We may want to ignore those and simply consider the map
    # for the general case, and let the caller decide it it wants further
    # filtering. We'll have to wait until the use case pops up.
    predicate = predicate or (lambda x, y, _: not level.is_blocked(x, y))

    path_map = DijkstraGrid.new(
        level.w, level.h, start_pos,
        *goals,
        predicate=predicate, cost_function=cost_function,
    )
    return path_map


# Optimization ideas:
# - Compute path map on a slice of the actual map, restrained by FOV
#   range ?

def get_path_to_target(start_pos, target_pos, level):
    """
    Compute shortest path to `target_pos` and yields all cells on said path.

    `start_pos` and `target_pos` should both be (x, y) tupples.

    """
    path_map = get_path_map(level, target_pos)

    x, y = start_pos
    while (x, y) != target_pos:
        x, y, _ = min(
            path_map.get_neighbors(x, y),
            key=lambda pos_dist_tupple: pos_dist_tupple[2])
        yield x, y


def get_step_to_target(start_pos, target_pos, level):
    """
    Compute shortest path to `target` and return a normalized vector
    pointing towards it.

    """
    step_x, step_y = next(get_path_to_target(start_pos, target_pos, level))
    return vector_to(*start_pos, step_x, step_y)
