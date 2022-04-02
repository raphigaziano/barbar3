import unittest
from unittest.mock import MagicMock, patch

from tests.unit.base import DummyRawsMixin

from barbarian.spawn import spawn_entity, build_spawn_table


class BaseSpawnTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        def _mock_component_class(cls, attr_name):
            cls.attr_name = attr_name
            return cls

        class MapMock(MagicMock):

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.__getitem__ = (
                    lambda self, k: _mock_component_class(
                        ComponentMock, attr_name=k)
                )

        class ComponentMock(MagicMock):
            __COMPONENT_MAP__ = MapMock()


        component_patcher = patch('barbarian.entity.Component', ComponentMock)
        mocked_component = component_patcher.start()

        isinstance_patcher = patch(
            'barbarian.entity.isinstance', return_value=False)
        isinstance_patcher.start()

        cls.addClassCleanup(component_patcher.stop)
        cls.addClassCleanup(isinstance_patcher.stop)


class TestSpawnEntity(BaseSpawnTest):

    _dummy_raws = {
        'actors': {
            'actor_1': {
                'foo': {'foo': 'oof'},
            },
            'actor_2': {
                'bar': {'bar': 'rab'},
            },
        },
        'props': {},
        'items': {
            'item_1': { 'woop': {'moop': 'meep'},
            }
        },
        'spawn': ['actor_1', 'actor_2', 'item_1'],
    }

    def test_spawn_entity(self):
        data = self._dummy_raws['actors']['actor_1']
        e = spawn_entity(0, 0, data)
        self.assertIsNotNone(e)
        self.assertEqual('oof', e.foo.foo)

        data = self._dummy_raws['actors']['actor_2']
        e = spawn_entity(0, 0, data)
        self.assertIsNotNone(e)
        self.assertEqual('rab', e.bar.bar)

        data = self._dummy_raws['items']['item_1']
        e = spawn_entity(0, 0, data)
        self.assertIsNotNone(e)
        self.assertEqual('meep', e.woop.moop)

    def test_set_position(self):
        data = self._dummy_raws['actors']['actor_1']
        e = spawn_entity(42, 86, data)
        self.assertEqual((42, 86), (e.pos.x, e.pos.y))

    def test_spawn_entity_no_op_if_data_is_none(self):
        e = spawn_entity(0, 0, None)
        self.assertIsNone(e)


class TestSpawnTable(unittest.TestCase):

    SPAWN_DATA = [
        {'name': 'entity_1', 'weight': 5},
        {'name': 'entity_2', 'weight': 5, 'depth_mod': 0},
        {'name': 'entity_3', 'weight': 5, 'depth_mod': 1},
        {'name': 'entity_4', 'weight': 5, 'depth_mod': 2},
        {'name': 'entity_5', 'weight': 5, 'depth_mod': -1},
    ]

    @patch('barbarian.spawn.get_spawn_data', return_value=SPAWN_DATA)
    def test_spawn_table(self, _):

        level = MagicMock()
        level.depth = 1

        st = build_spawn_table(level)
        self.assertEqual((5, 'entity_1'), st[0])
        self.assertEqual((5, 'entity_2'), st[1])
        self.assertEqual((6, 'entity_3'), st[2])
        self.assertEqual((7, 'entity_4'), st[3])
        self.assertEqual((4, 'entity_5'), st[4])

        level.depth = 3

        st = build_spawn_table(level)
        self.assertEqual((5, 'entity_1'), st[0])
        self.assertEqual((5, 'entity_2'), st[1])
        self.assertEqual((8, 'entity_3'), st[2])
        self.assertEqual((11, 'entity_4'), st[3])
        self.assertEqual((2, 'entity_5'), st[4])

        level.depth = 10

        st = build_spawn_table(level)
        self.assertEqual((5, 'entity_1'), st[0])
        self.assertEqual((5, 'entity_2'), st[1])
        self.assertEqual((15, 'entity_3'), st[2])
        self.assertEqual((25, 'entity_4'), st[3])
        self.assertEqual((0, 'entity_5'), st[4])

    SPAWN_DATA = [
        {'name': 'entity_1', 'weight': 1, 'depth_mod': 0.5},
        {'name': 'entity_2', 'weight': 1, 'depth_mod': 1.5},
    ]

    @patch('barbarian.spawn.get_spawn_data', return_value=SPAWN_DATA)
    def test_float_values_for_depth_mod(self, _):

        level = MagicMock()
        level.depth = 1

        st = build_spawn_table(level)
        self.assertEqual((1.5, 'entity_1'), st[0])
        self.assertEqual((2.5, 'entity_2'), st[1])

        level.depth = 3

        st = build_spawn_table(level)
        self.assertEqual((2.5, 'entity_1'), st[0])
        self.assertEqual((5.5, 'entity_2'), st[1])

    SPAWN_DATA = [
        {'name': 'entity_1', 'weight': 1, 'depth_mod': -2},
    ]

    @patch('barbarian.spawn.get_spawn_data', return_value=SPAWN_DATA)
    def test_ensure_no_negative_values(self, _):

        level = MagicMock()
        level.depth = 1

        st = build_spawn_table(level)
        self.assertEqual((0, 'entity_1'), st[0])
