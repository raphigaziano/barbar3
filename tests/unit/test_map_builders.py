import unittest

from barbarian.map import Map
from barbarian.genmap.common import BaseMapBuilder


class TestMap(unittest.TestCase):

    def test_snapshots(self):
        builder = BaseMapBuilder(debug=True)
        m = Map(3, 3)
        builder.take_snapshot(m)
        self.assertEqual(len(builder.snapshots), 1)
        self.assertEqual(builder.snapshots[0].cells, m.cells)

        m[1, 1] = 'woot'
        builder.take_snapshot(m)
        self.assertEqual(len(builder.snapshots), 2)
        self.assertNotEqual(builder.snapshots[0].cells, m.cells)
        self.assertEqual(builder.snapshots[1].cells, m.cells)

    def test_snoapshot_is_a_noop_in_non_debug_mode(self):
        builder = BaseMapBuilder(debug=False)
        builder.take_snapshot('dummy_snapshot')
        self.assertEqual(len(builder.snapshots), 0)
