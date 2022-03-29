import unittest
from unittest.mock import Mock

from barbarian.systems.visibility import spot_player


class TestSpotPlayer(unittest.TestCase):

    def test_actor_uses_its_own_fov_if_set(self):

        actor = Mock()
        actor.fov.visible_cells = []
        player = Mock()

        spot_player(actor, player)

        player.fov.is_in_fov.assert_not_called()

    def test_fallback_on_player_fov_if_no_fov(self):

        actor = Mock()
        actor.fov = None
        player = Mock()

        spot_player(actor, player)

        player.fov.is_in_fov.assert_called()
