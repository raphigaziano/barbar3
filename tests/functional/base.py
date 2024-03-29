import unittest
from unittest.mock import patch

from barbarian import settings
from barbarian.components import init_components
from barbarian.world import Level
from barbarian.map import Map, TileType
from barbarian.raws import get_entity_data
from barbarian.spawn import spawn_entity


class BaseFunctionalTestCase(unittest.TestCase):
    """ Base test case for functional tests, providing commone helpers. """

    test_raws_root = 'tests/raws/path'
    dummy_map = ('.',)

    def setUp(self):
        init_components()
        raws_root_patcher = patch(
            'barbarian.settings.RAWS_ROOT', self.test_raws_root)
        raws_root_patcher.start()

        self.addCleanup(raws_root_patcher.stop)

    def build_dummy_level(self):

        if not hasattr(self, 'dummy_map'):
            self.fail(
                'Test setup error: TestCases must defined a dummy_map '
                'attribute to use the build_dummy_level helper.')

        h = len(self.dummy_map)
        w = len(self.dummy_map[0])

        level = Level(w, h)
        level.map = Map(w, h, [
            TileType(char) for row in self.dummy_map for char in row
        ])
        level.init_fov_map()

        return level

    def spawn_actor(self, x, y, actor_name):
        data = get_entity_data(actor_name, 'actors')
        return spawn_entity(x, y, data)

    def spawn_prop(self, x, y, prop_name):
        data = get_entity_data(prop_name, 'props')
        return spawn_entity(x, y, data)

    def spawn_item(self, x, y, item_name):
        data = get_entity_data(item_name, 'items')
        return spawn_entity(x, y, data)

    def actor_list(self, x, y, *entity_names):
        for ename in entity_names:
            yield self.spawn_actor(x, y, ename)

    def prop_list(self, x, y, *entity_names):
        for ename in entity_names:
            yield self.spawn_prop(x, y, ename)

    def item_list(self, x, y, *entity_names):
        for ename in entity_names:
            yield self.spawn_item(x, y, ename)

    def assert_action_accepted(self, caller, action, *args, **kwargs):
        res = caller(action, *args, **kwargs)
        self.assertTrue(action.processed)
        self.assertTrue(action.valid)
        return res

    def assert_action_rejected(self, caller, action, *args, **kwargs):
        res = caller(action, *args, **kwargs)
        self.assertTrue(action.processed)
        self.assertFalse(action.valid)
        return res
