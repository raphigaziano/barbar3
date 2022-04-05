import unittest
import random

from barbarian.utils.rng import Rng
from barbarian.map import Map
from barbarian.genmap import _MAP_BUILDERS
from barbarian.genmap.common import BaseMapBuilder


class TestSnapshots(unittest.TestCase):

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


class TestWorldGenesis(unittest.TestCase):

    MAP_W, MAP_H = 30, 30

    def test_mapgen_is_deterministic(self):

        Rng.init_root()
        Rng.add_rng('dungeon')
        Rng.add_rng('spawn')

        # Save rng state
        rng_state = Rng.dungeon.getstate()

        # Generate one map for each builder. Rngs were initialized without a 
        # seed, so map will be actually random.

        no_perturb_maps = []

        for BuilderCls in _MAP_BUILDERS:
            builder = BuilderCls(debug=False)
            no_perturb_maps.append(
                builder.build_map(self.MAP_W, self.MAP_H, 0))

        # Reset rng state
        Rng.dungeon.setstate(rng_state)

        # Rebuild the same map, but spam calls to various random generators 
        # along the way

        perturb_maps = []

        for i, BuilderCls in enumerate(_MAP_BUILDERS):

            # Random mess \o/
            Rng.randint(0, random.randint(2, 10))
            Rng.spawn.roll_dice_str(f'{i}D{i*2}+3')
            random.randrange(Rng.roll_dice_str(f'2d{i+1}'))
            Rng.spawn.choice([random.random() for _ in range(i+1)])

            builder = BuilderCls(debug=False)
            perturb_maps.append(
                builder.build_map(self.MAP_W, self.MAP_H, 0))

        # Compare results...

        self.assertEqual(len(no_perturb_maps), len(perturb_maps))

        for unperturbed, perturbed in zip(no_perturb_maps, perturb_maps):
            for x, y, c in unperturbed:
                self.assertEqual(c, perturbed[x,y])
