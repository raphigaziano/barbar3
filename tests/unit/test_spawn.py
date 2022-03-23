import unittest
from unittest.mock import MagicMock, patch

from tests.unit.base import DummyRawsMixin

from barbarian.utils.rng import Rng
from barbarian.spawn import spawn_entity, spawn_door, spawn_zone, spawn_level
from barbarian.settings import MAX_SPAWNS


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
