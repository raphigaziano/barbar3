def idx_to_c(idx, width):
    """ Convert array index to cartesian coordinates. """
    return idx % width, idx // width

def c_to_idx(x, y, width):
    """ Convert cartesian coordinates to internal array index. """
    return x + (y * width)


def vector_to(start_x, start_y, end_x, end_y, normalize=True):

    dx, dy = end_x - start_x, end_y - start_y
    if not normalize:
        return dx, dy

    vx = vy = 0

    if dx > 0:      vx = 1
    elif dx < 0:    vx = -1

    if dy > 0:      vy = 1
    elif dy < 0:    vy = -1

    return start_x + vx, start_y + vy


def closest_open_cell(x, y, map_width, map_height, pathmap,
                      cost_modifier=None, predicate=None):
    closest_x, closest_y = None, None
    closest_distance =    10000
    lowest_map_distance = 10000

    for mx in range(map_width):
        for my in range(map_height):
            midx = c_to_idx(mx, my, map_width)
            import sys
            if pathmap[midx] == sys.maxsize:
                continue
            if predicate is not None and not predicate(midx):
                continue
            dist = (mx - x)*(mx - x) + (my - y)*(my - y)
            if cost_modifier is not None:
                dist = cost_modifier(midx, dist)
            if (dist < closest_distance or
                (dist == closest_distance and pathmap[midx] < lowest_map_distance)
            ):
                closest_x, closest_y = mx, my
                closest_distance = dist
                lowest_map_distance = pathmap[midx]

    return closest_x, closest_y


def path_to(from_x, from_y, to_x, to_y, map_w, pathmap):

    cx, cy = from_x, from_y

    while (cx, cy) != (to_x, to_y):
        yield cx, cy
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
            if c_to_idx(nx, ny, map_w) >= len(pathmap):
                continue
            if (pathmap[c_to_idx(nx, ny, map_w)] <
                pathmap[c_to_idx(cx, cy, map_w)]
            ):
                cx, cy = nx, ny
                break
        else:
            cx, cy = vector_to(cx, cy, to_x, to_y)


def closest_entities(
        entity_list, map_width, cell_mask, distance_map, exclude_player=True
):
    l = []
    for e in entity_list:
        if exclude_player and e['actor']['is_player']:
            continue
        map_idx = c_to_idx(*e['pos'], map_width)
        if cell_mask[map_idx]:
            l.append((distance_map[map_idx], e))
    return [e for _, e in sorted(l, key=lambda t: t[0])]

