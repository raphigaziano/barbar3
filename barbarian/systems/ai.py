"""
Ai routines.

"""
from barbarian.utils.geometry import vector_to
from barbarian.utils.rng import Rng
from barbarian.actions import Action, ActionType


def _spot_player(actor, player):
    """
    Can `actor` see the player ?

    Try and use the actor's own fov, and falls back to a simple
    'if the player can see me, then I can see him' check if actor has
    no fov.

    """
    if actor.fov:
        return (player.pos.x, player.pos.y) in actor.fov.visible_cells
    return player.fov.is_in_fov(actor.pos.x, actor.pos.y)


def tmp_ai(actor, game):
    """ Temporary, *very dumb* ai. """
    if actor.is_player:
        return Action(ActionType.REQUEST_INPUT)

    if _spot_player(actor, game.player):
        dx, dy = vector_to(
            actor.pos.x, actor.pos.y, game.player.pos.x, game.player.pos.y)
        return Action.move(actor, d={'dir': (dx, dy)})

    # Can't spot the player, so move randomly
    # return Action(type=ActionType.XPLORE, actor=actor)
    dx = Rng.choice([-1, 0, 1])
    dy = Rng.choice([-1, 0, 1])
    return Action.move(actor, d={'dir': (dx, dy)})
