import unittest

from barbarian.utils.geometry import bresenham


# Copied from https://github.com/encukou/bresenham
class TestBresenham(unittest.TestCase):

    def test_brenenham(self):

        params_and_expected_results = (
            (0, 0, 0, 0,
                ((0, 0), )),
            (0, 0, 5, 0,
                ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0))),
            (0, 0, -5, 0,
                ((0, 0), (-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0))),
            (0, 0, 0, 5,
                ((0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5))),
            (0, 0, 0, -5,
                ((0, 0), (0, -1), (0, -2), (0, -3), (0, -4), (0, -5))),
            (0, 0, 2, 3,
                ((0, 0), (1, 1), (1, 2), (2, 3))),
            (0, 0, -2, 3,
                ((0, 0), (-1, 1), (-1, 2), (-2, 3))),
            (0, 0, 2, -3,
                ((0, 0), (1, -1), (1, -2), (2, -3))),
            (0, 0, -2, -3,
                ((0, 0), (-1, -1), (-1, -2), (-2, -3))),
            (-1, -3, 3, 3,
                ((-1, -3), (0, -2), (0, -1),
                 (1, 0), (2, 1), (2, 2), (3, 3))),
            (0, 0, 11, 1,
                ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0),
                 (6, 1), (7, 1), (8, 1), (9, 1), (10, 1), (11, 1))),
        )
        for x0, y0, x1, y1, expected in params_and_expected_results:
            self.assertEqual(
                tuple(bresenham(x0, y0, x1, y1)), expected)
            self.assertEqual(
                tuple(bresenham(x1, y1, x0, y0)), tuple(reversed(expected)))

    def test_min_slope_two_way(self):

        self.assertEqual(
            tuple(bresenham(0, 0, 10, 1)),
            ((0, 0), (1, 0), (2, 0), (3, 0),
             (4, 0), (5, 1), (6, 1), (7, 1),
             (8, 1), (9, 1), (10, 1))
        )
        self.assertEqual(
            tuple(bresenham(10, 1, 0, 0)),
            ((10, 1), (9, 1), (8, 1), (7, 1),
             (6, 1), (5, 0), (4, 0), (3, 0),
             (2, 0), (1, 0), (0, 0))
        )
