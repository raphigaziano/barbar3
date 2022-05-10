from pprint import pprint

from tests.functional.base import BaseFunctionalTestCase

from barbarian.components.actor import Fov


class FovTest(BaseFunctionalTestCase):

    _fov_glyphs = {True: '.', False: '_'}

    def _print_fov_map(self, fov_map):
        for x, y, c in fov_map:
            glyph = self._fov_glyphs[c.in_fov]
            print(glyph, end='')
            if x == fov_map.w - 1:
                print()
        print()

    def check_fov_map(self, str_map, fov_map):
        self._print_fov_map(fov_map)
        for x, y, cell in fov_map:
            if str_map[y][x] == '.':
                self.assertTrue(cell.in_fov)
            elif str_map[y][x] == '_':
                self.assertFalse(cell.in_fov)

    def test_fov_open_map(self):

        dummy_map = (
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
        )
        expected = (
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
        )

        level = self.build_dummy_level(dummy_map)
        # map center = (4, 4)
        level.fov_map.compute(4, 4, radius=10, light_walls=True)
        self.check_fov_map(expected, level.fov_map)

    def test_fov_closed_map_light_walls(self):

        dummy_map = (
            '##########',
            '##########',
            '##########',
            '##########',
            '####.#####',
            '##########',
            '##########',
            '##########',
            '##########',
            '##########',
        )
        expected = (
            '__________',
            '__________',
            '__________',
            '___...____',
            '___...____',
            '___...____',
            '__________',
            '__________',
            '__________',
            '__________',
        )

        level = self.build_dummy_level(dummy_map)
        # map center = (4, 4)
        level.fov_map.compute(4, 4, radius=10, light_walls=True)
        self.check_fov_map(expected, level.fov_map)

    def test_fov_closed_map_no_light_walls(self):

        dummy_map = (
            '##########',
            '##########',
            '##########',
            '##########',
            '####.#####',
            '##########',
            '##########',
            '##########',
            '##########',
            '##########',
        )
        expected = (
            '__________',
            '__________',
            '__________',
            '__________',
            '____._____',
            '__________',
            '__________',
            '__________',
            '__________',
            '__________',
        )

        level = self.build_dummy_level(dummy_map)
        # map center = (4, 4)
        level.fov_map.compute(4, 4, radius=10, light_walls=False)
        self.check_fov_map(expected, level.fov_map)

    def test_fov_range(self):

        dummy_map = (
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
        )
        expected = (
            '__________',
            '____._____',
            '__.....___',
            '__.....___',
            '_.......__',
            '__.....___',
            '__.....___',
            '____._____',
            '__________',
            '__________',
        )

        level = self.build_dummy_level(dummy_map)
        # map center = (4, 4)
        level.fov_map.compute(4, 4, radius=3, light_walls=False)
        self.check_fov_map(expected, level.fov_map)

    def test_fov_pillars(self):

        # Adjacent pillars

        # Adjacent NW
        dummy_map = (
            '..........',
            '..........',
            '..........',
            '...#......',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
        )
        expected = (
            '___.......',
            '___.......',
            '___.......',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
        )

        level = self.build_dummy_level(dummy_map)
        # map center = (4, 4)
        level.fov_map.compute(4, 4, radius=10, light_walls=True)
        self.check_fov_map(expected, level.fov_map)

        # Adjacent N
        dummy_map = (
            '..........',
            '..........',
            '..........',
            '....#.....',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
        )
        expected = (
            '...___....',
            '...___....',
            '...._.....',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
        )

        level = self.build_dummy_level(dummy_map)
        # map center = (4, 4)
        level.fov_map.compute(4, 4, radius=10, light_walls=True)
        self.check_fov_map(expected, level.fov_map)

        # Adjacent NE
        dummy_map = (
            '..........',
            '..........',
            '..........',
            '.....#....',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
        )
        expected = (
            '......____',
            '......____',
            '......__..',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
        )

        level = self.build_dummy_level(dummy_map)
        # map center = (4, 4)
        level.fov_map.compute(4, 4, radius=10, light_walls=True)
        self.check_fov_map(expected, level.fov_map)

        # Adjacent E
        dummy_map = (
            '..........',
            '..........',
            '..........',
            '..........',
            '.....#....',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
        )
        expected = (
            '..........',
            '..........',
            '........._',
            '.......___',
            '......____',
            '.......___',
            '........._',
            '..........',
            '..........',
            '..........',
        )

        level = self.build_dummy_level(dummy_map)
        # map center = (4, 4)
        level.fov_map.compute(4, 4, radius=10, light_walls=True)
        self.check_fov_map(expected, level.fov_map)

        # Adjacent SE
        dummy_map = (
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '.....#....',
            '..........',
            '..........',
            '..........',
            '..........',
        )
        expected = (
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '......__..',
            '......____',
            '.......___',
            '.......___',
        )

        level = self.build_dummy_level(dummy_map)
        # map center = (4, 4)
        level.fov_map.compute(4, 4, radius=10, light_walls=True)
        self.check_fov_map(expected, level.fov_map)

        # Adjacent S
        dummy_map = (
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '....#.....',
            '..........',
            '..........',
            '..........',
            '..........',
        )
        expected = (
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '...._.....',
            '...___....',
            '...___....',
            '.._____...',
        )

        level = self.build_dummy_level(dummy_map)
        # map center = (4, 4)
        level.fov_map.compute(4, 4, radius=10, light_walls=True)
        self.check_fov_map(expected, level.fov_map)

        # Adjacent SW
        dummy_map = (
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '...#......',
            '..........',
            '..........',
            '..........',
            '..........',
        )
        expected = (
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '___.......',
            '___.......',
            '__........',
            '__........',
        )

        level = self.build_dummy_level(dummy_map)
        # map center = (4, 4)
        level.fov_map.compute(4, 4, radius=10, light_walls=True)
        self.check_fov_map(expected, level.fov_map)

        # Adjacent W
        dummy_map = (
            '..........',
            '..........',
            '..........',
            '..........',
            '...#......',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
        )
        expected = (
            '..........',
            '..........',
            '..........',
            '__........',
            '___.......',
            '__........',
            '..........',
            '..........',
            '..........',
            '..........',
        )

        level = self.build_dummy_level(dummy_map)
        # map center = (4, 4)
        level.fov_map.compute(4, 4, radius=10, light_walls=True)
        self.check_fov_map(expected, level.fov_map)

        # Non adjacent pillars

        # Non-adjacent NW
        dummy_map = (
            '..........',
            '..........',
            '..#.......',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
        )
        expected = (
            '__........',
            '__........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
        )

        level = self.build_dummy_level(dummy_map)
        # map center = (4, 4)
        level.fov_map.compute(4, 4, radius=10, light_walls=True)
        self.check_fov_map(expected, level.fov_map)

        # Non-adjacent N
        dummy_map = (
            '..........',
            '..........',
            '....#.....',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
        )
        expected = (
            '...._.....',
            '...._.....',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
        )

        level = self.build_dummy_level(dummy_map)
        # map center = (4, 4)
        level.fov_map.compute(4, 4, radius=10, light_walls=True)
        self.check_fov_map(expected, level.fov_map)

        # Non-adjacent NE
        dummy_map = (
            '..........',
            '..........',
            '......#...',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
        )
        expected = (
            '.......___',
            '......._..',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
        )

        level = self.build_dummy_level(dummy_map)
        # map center = (4, 4)
        level.fov_map.compute(4, 4, radius=10, light_walls=True)
        self.check_fov_map(expected, level.fov_map)

        # Non-adjacent E
        dummy_map = (
            '..........',
            '..........',
            '..........',
            '..........',
            '......#...',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
        )
        expected = (
            '..........',
            '..........',
            '..........',
            '........._',
            '.......___',
            '........._',
            '..........',
            '..........',
            '..........',
            '..........',
        )

        level = self.build_dummy_level(dummy_map)
        # map center = (4, 4)
        level.fov_map.compute(4, 4, radius=10, light_walls=True)
        self.check_fov_map(expected, level.fov_map)

        # Non-adjacent SE
        dummy_map = (
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '......#...',
            '..........',
            '..........',
            '..........',
        )
        expected = (
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '......._..',
            '........_.',
            '........._',
        )

        level = self.build_dummy_level(dummy_map)
        # map center = (4, 4)
        level.fov_map.compute(4, 4, radius=10, light_walls=True)
        self.check_fov_map(expected, level.fov_map)

        # Non-adjacent S
        dummy_map = (
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '....#.....',
            '..........',
            '..........',
            '..........',
        )
        expected = (
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '...._.....',
            '...._.....',
            '...___....',
        )

        level = self.build_dummy_level(dummy_map)
        # map center = (4, 4)
        level.fov_map.compute(4, 4, radius=10, light_walls=True)
        self.check_fov_map(expected, level.fov_map)

        # Non-adjacent SW
        dummy_map = (
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..#.......',
            '..........',
            '..........',
            '..........',
        )
        expected = (
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '__........',
            '_.........',
            '_.........',
        )

        level = self.build_dummy_level(dummy_map)
        # map center = (4, 4)
        level.fov_map.compute(4, 4, radius=10, light_walls=True)
        self.check_fov_map(expected, level.fov_map)

        # Non-adjacent W
        dummy_map = (
            '..........',
            '..........',
            '..........',
            '..........',
            '..#.......',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
        )
        expected = (
            '..........',
            '..........',
            '..........',
            '..........',
            '__........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
        )

        level = self.build_dummy_level(dummy_map)
        # map center = (4, 4)
        level.fov_map.compute(4, 4, radius=10, light_walls=True)
        self.check_fov_map(expected, level.fov_map)

    def test_base_dungeon_layouts(self):

        dummy_map = (
            '......####',
            '......#...',
            '..##.##...',
            '..#.......',
            '###.......',
            '..........',
            '#..####.##',
            '#..#..#.#.',
            '####..#.#.',
            '......#.#.',
        )
        expected = (
            '____.___..',
            '____.___..',
            '__........',
            '__........',
            '..........',
            '..........',
            '..........',
            '....____._',
            '....______',
            '__________',
        )

        level = self.build_dummy_level(dummy_map)
        # map center = (4, 4)
        level.fov_map.compute(4, 4, radius=10, light_walls=True)
        self.check_fov_map(expected, level.fov_map)

        # ... Other layouts ???

    def test_wall_artifacts_postprocessing(self):

        dummy_map = (
            '...#.#....',
            '...#.#....',
            '...#.#....',
            '####.#####',
            '..........',
            '####.#####',
            '...#.#....',
            '...#.#....',
            '...#.#....',
            '...#.#....',
        )
        expected = (
            '___...____',
            '___...____',
            '___...____',
            '..........',
            '..........',
            '..........',
            '___...____',
            '___...____',
            '___...____',
            '___...____',
        )

        level = self.build_dummy_level(dummy_map)
        # map center = (4, 4)
        level.fov_map.compute(4, 4, radius=10, light_walls=True)
        self.check_fov_map(expected, level.fov_map)


class TestActorFov(BaseFunctionalTestCase):

    def test_actor_fov(self):

        dummy_map = (
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
        )
        level = self.build_dummy_level(dummy_map)
        actor = self.spawn_actor(4, 4, 'orc')
        actor.add_component('fov', Fov(range=10))

        actor.fov.compute(level, actor.pos.x, actor.pos.y)
        for x, y, _ in level.map:
            self.assertIn((x, y), actor.fov.visible_cells)
            self.assertIn((x, y), actor.fov.explored)

    def test_explored_cells_are_remembered(self):

        dummy_map = (
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
        )
        level = self.build_dummy_level(dummy_map)
        actor = self.spawn_actor(4, 4, 'orc')
        actor.add_component('fov', Fov(range=10))

        # First check, all cells visible
        actor.fov.compute(level, actor.pos.x, actor.pos.y)

        # Reduce FOV range for second check
        actor.fov.range = 1
        actor.fov.compute(level, actor.pos.x, actor.pos.y)

        # All cells are still explored
        for x, y, _ in level.map:
            self.assertIn((x, y), actor.fov.explored)

    def test_update_level(self):

        dummy_map = (
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
            '..........',
        )
        level = self.build_dummy_level(dummy_map)
        actor = self.spawn_actor(4, 4, 'orc')
        actor.add_component('fov', Fov(range=10))

        # First check, update_level = False => No explored cells on the level
        actor.fov.compute(level, actor.pos.x, actor.pos.y, update_level=False)
        self.assertEqual(0, len(level.explored))

        # Second check, update_level = True => all cells are explored on the level
        actor.fov.compute(level, actor.pos.x, actor.pos.y, update_level=True)
        for x, y, _ in level.map:
            self.assertIn((x, y), level.explored)

        # Reduce FOV range for third check (relpicate above test)
        actor.fov.range = 1
        actor.fov.compute(level, actor.pos.x, actor.pos.y, update_level=False)

        # All cells are still explored
        for x, y, _ in level.map:
            self.assertIn((x, y), level.explored)
