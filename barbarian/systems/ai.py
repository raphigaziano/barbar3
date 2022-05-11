"""
Ai routines.

"""
from barbarian.utils.rng import Rng
from barbarian.utils.geometry import distance_from, vector_to
from barbarian.actions import Action, ActionType
from barbarian.systems.visibility import spot_player
from barbarian.pathfinding import PathBlockedError, get_step_to_player


def tmp_ai(actor, game):
    """ Temporary, *very dumb* ai. """
    level = game.current_level

    if spot_player(actor, player := game.player):

        ap, tp = actor.pos, player.pos

        # Attack (melee) if we're next to the player
        if distance_from(ap.x, ap.y, tp.x, tp.y) == 1:
            return Action.attack(actor, player)

        # Move towards player
        try:
            dx, dy = get_step_to_player((ap.x, ap.y), (tp.x, tp.y), level)
            vx, vy = vector_to(ap.x, ap.y, dx, dy)
            return Action.move(actor, d={'dir': (vx, vy)})
        except PathBlockedError:
            # Path to player is blocked: fallback to dumb vector based
            # pathfinding to try and move towards the player anyway
            vx, vy = vector_to(ap.x, ap.y, tp.x, tp.y)
            # Avoid bumping into other mobs
            if not level.is_blocked(ap.x + vx, ap.y + vy):
                return Action.move(actor, d={'dir': (vx, vy)})
            # Dumb path also blocked: no-op (will fall back to random move)

    # Can't spot the player, so move randomly
    # return Action(type=ActionType.XPLORE, actor=actor)
    neighbor_cells = list(level.map.get_neighbors(actor.pos.x, actor.pos.y))
    while neighbor_cells:
        dx, dy, _ = Rng.choice(neighbor_cells)
        if level.is_blocked(dx, dy):
            neighbor_cells.remove((dx, dy, _))
            continue
        vx, vy = vector_to(actor.pos.x, actor.pos.y, dx, dy)
        return Action.move(actor, d={'dir': (vx, vy)})

    # No possible move: 
    return Action(ActionType.IDLE)
