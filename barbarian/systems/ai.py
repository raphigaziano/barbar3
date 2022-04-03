"""
Ai routines.

"""
from barbarian.utils.rng import Rng
from barbarian.actions import Action, ActionType
from barbarian.systems.visibility import spot_player
from barbarian.pathfinding import get_step_to_target


def tmp_ai(actor, game):
    """ Temporary, *very dumb* ai. """
    if actor.is_player:
        return Action(ActionType.REQUEST_INPUT)

    if spot_player(actor, player := game.player):
        dx, dy = get_step_to_target(
            (actor.pos.x, actor.pos.y), (player.pos.x, player.pos.y),
            game.current_level)
        return Action.move(actor, d={'dir': (dx, dy)})

    # Can't spot the player, so move randomly
    # return Action(type=ActionType.XPLORE, actor=actor)
    dx = Rng.choice([-1, 0, 1])
    dy = Rng.choice([-1, 0, 1])
    return Action.move(actor, d={'dir': (dx, dy)})
