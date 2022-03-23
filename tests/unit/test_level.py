import unittest
from unittest.mock import Mock, patch

from barbarian.utils.rng import Rng
from barbarian.map import Map, TileType
from barbarian.world import Level


class TestLevel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Rng.add_rng('dungeon')

    def _get_entity_mock(self, blocks=True, blocks_sight=False):
        me = Mock()
        me.physics.blocks = blocks
        me.physics.blocks_sight = blocks_sight
        return me

    def test_init_fov_map(self):
        l = Level(10, 10)
        l.map = Map(l.w, l.h, [TileType.FLOOR] * (l.w * l.h))
        l.map[5, 5] = TileType.WALL

        l.actors.add(
            0, 0, self._get_entity_mock(blocks_sight=True))
        l.actors.add(
            1, 1, self._get_entity_mock(blocks_sight=False))
        l.props.add(
            2, 2, self._get_entity_mock(blocks_sight=True))
        l.props.add(
            3, 3, self._get_entity_mock(blocks_sight=False))

        l.actors.add(
            9, 9, self._get_entity_mock(blocks_sight=False))
        l.props.add(
            9, 9, self._get_entity_mock(blocks_sight=True))

        l.init_fov_map()

        self.assertFalse(l.fov_map.transparent[5,5])

        self.assertFalse(l.fov_map.transparent[0,0])
        self.assertTrue(l.fov_map.transparent[1,1])
        self.assertFalse(l.fov_map.transparent[2,2])
        self.assertTrue(l.fov_map.transparent[3,3])

        self.assertFalse(l.fov_map.transparent[9, 9])

    def test_is_blocked(self):

        # Simple defering to Map
        l = Level(10, 10)
        l.map = Map(l.w, l.h, [TileType.WALL] * (l.w * l.h))
        for x, y, _ in l.map:
            self.assertTrue(l.is_blocked(x, y))

        l = Level(10, 10)
        l.map = Map(l.w, l.h, [TileType.FLOOR] * (l.w * l.h))
        for x, y, _ in l.map:
            self.assertFalse(l.is_blocked(x, y))

        # Blocking actor 
        l.actors.add(0, 0, self._get_entity_mock(blocks=True))
        self.assertTrue(l.is_blocked(0, 0))
        # Non-blocking actor 
        l.actors.add(1, 1, self._get_entity_mock(blocks=False))
        self.assertFalse(l.is_blocked(1, 1))

        # Blocking prop
        l.props.add(2, 2, self._get_entity_mock(blocks=True))
        self.assertTrue(l.is_blocked(2, 2))
        # Non-locking prop
        l.props.add(3, 3, self._get_entity_mock(blocks=False))
        self.assertFalse(l.is_blocked(3, 3))

        # Non-blocking prop + blocking actor
        l.props.add(4, 4, self._get_entity_mock(blocks=False))
        l.actors.add(4, 4, self._get_entity_mock(blocks=True))
        self.assertTrue(l.is_blocked(4, 4))

        # Blocking prop + non-blocking actor
        l.props.add(0, 4, self._get_entity_mock(blocks=True))
        l.actors.add(0, 4, self._get_entity_mock(blocks=False))
        self.assertTrue(l.is_blocked(0, 4))

    def test_is_blocked_out_of_bounds(self):

        l = Level(10, 10)
        l.map = Map(l.w, l.h, [TileType.FLOOR] * (l.w * l.h))

        self.assertTrue(l.is_blocked(-1, -1))
        self.assertTrue(l.is_blocked(10, 10))
        self.assertTrue(l.is_blocked(0, -1))
        self.assertTrue(l.is_blocked(10, 0))

    def test_move_actor(self):
        l = Level(10, 10)
        l.map = Map(l.w, l.h, [TileType.FLOOR] * (l.w * l.h))

        actor = self._get_entity_mock()
        actor.pos.x = 1
        actor.pos.y = 1
        l.actors[1, 1] = actor

        res = l.move_actor(actor, 1, 1)
        self.assertTrue(res)
        self.assertEqual((2, 2), (actor.pos.x, actor.pos.y))
        self.assertIsNone(l.actors[1, 1])
        self.assertEqual(actor, l.actors[2, 2])

    def test_move_actor_failue(self):
        l = Level(10, 10)
        l.map = Map(l.w, l.h, [TileType.FLOOR] * (l.w * l.h))
        l.map[2, 2] = TileType.WALL

        actor = self._get_entity_mock()
        actor.pos.x = 1
        actor.pos.y = 1
        l.actors[1, 1] = actor

        res = l.move_actor(actor, 1, 1)
        self.assertFalse(res)
        self.assertEqual((1, 1), (actor.pos.x, actor.pos.y))
        self.assertEqual(actor, l.actors[1, 1])
        self.assertIsNone(l.actors[2, 2])

    def test_enter_level(self):

        for is_player in (True, False):
            l = Level(10, 10)

            actor = self._get_entity_mock()
            actor.pos.x = 5
            actor.pos.y = 5
            actor.fov = Mock()
            actor.is_player = is_player

            l.enter(actor)

            self.assertEqual(actor, l.actors[5, 5])
            actor.fov.reset.assert_called_once()
            actor.fov.compute.assert_called_once_with(
                l, 5, 5, update_level=is_player)
