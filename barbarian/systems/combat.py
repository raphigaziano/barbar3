"""
Murder logic yay

"""
import logging

from barbarian.actions import Action


logger = logging.getLogger(__name__)


def attack(attack_action):
    """ Handle actor attacking another. """
    actor, target, _ = attack_action.unpack()
    attack_action.accept()

    stats_a, stats_t = actor.stats, target.stats
    dmg = max(1, stats_a.strength - stats_t.strength)

    return Action.inflict_dmg(actor, target, {'dmg': dmg})
