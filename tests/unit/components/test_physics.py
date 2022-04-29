import unittest

from barbarian.components.physics import Position


class TestPosition(unittest.TestCase):

    def test_tupple_equality(self):
        pos = Position(x=2, y=4)
        self.assertEqual((2, 4), pos)
        self.assertEqual(Position(2, 4), pos)

        self.assertNotEqual((2, 3), pos)
        self.assertNotEqual((3, 2), pos)

