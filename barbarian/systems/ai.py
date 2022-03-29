"""
Ai routines.

"""
from barbarian.utils.geometry import vector_to
from barbarian.utils.rng import Rng
from barbarian.actions import Action, ActionType
from barbarian.systems.visibility import spot_player


def tmp_ai(actor, game):
    """ Temporary, *very dumb* ai. """
    if actor.is_player:
        return Action(ActionType.REQUEST_INPUT)

    if spot_player(actor, game.player):
        dx, dy = vector_to(
            actor.pos.x, actor.pos.y, game.player.pos.x, game.player.pos.y)
        return Action.move(actor, d={'dir': (dx, dy)})

    # Can't spot the player, so move randomly
    # return Action(type=ActionType.XPLORE, actor=actor)
    dx = Rng.choice([-1, 0, 1])
    dy = Rng.choice([-1, 0, 1])
    return Action.move(actor, d={'dir': (dx, dy)})
