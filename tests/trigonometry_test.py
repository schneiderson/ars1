import unittest
import math
from bot import trigonometry as tri

__author__ = 'Camiel Kerkhofs'

class TestTrigonometry(unittest.TestCase):

    def test_line_intersection(self):
        tmp = tri.line_intersect((10, 10), (20, 10), (10, 20), (20, 20))
        self.assertEqual(tmp, False)

        tmp = tri.line_intersect((10, 10), (20, 20), (50, 5), (20, 18))
        self.assertEqual(tmp, False)

        tmp = tri.line_intersect((10, 10), (20, 20), (10, 8), (20, 22))
        self.assertEqual(tmp, (15, 15))

        tmp = tri.line_intersect((10, 10), (20, 30), (10, 0), (20, 40))
        self.assertEqual(tmp, (15, 20))

    def test_line_endpoint(self):
        endpoint = tri.line_endpoint((0, 0), 0, 100)
        self.assertEqual((round(endpoint[0]), round(endpoint[1])), (100, 0))

        endpoint = tri.line_endpoint((0, 0), 45, 100)
        self.assertEqual((round(endpoint[0]), round(endpoint[1])), (71, 71))

        endpoint = tri.line_endpoint((0, 0), 90, 100)
        self.assertEqual((round(endpoint[0]), round(endpoint[1])), (0, 100))

        endpoint = tri.line_endpoint((0, 0), 135, 100)
        self.assertEqual((round(endpoint[0]), round(endpoint[1])), (-71, 71))

        endpoint = tri.line_endpoint((0, 0), 180, 100)
        self.assertEqual((round(endpoint[0]), round(endpoint[1])), (-100, 0))

        endpoint = tri.line_endpoint((0, 0), 225, 100)
        self.assertEqual((round(endpoint[0]), round(endpoint[1])), (-71, -71))

        endpoint = tri.line_endpoint((0, 100), 270, 100)
        self.assertEqual((round(endpoint[0]), round(endpoint[1])), (0, 0))

        endpoint = tri.line_endpoint((100, 100), 350, 100)
        self.assertEqual((round(endpoint[0]), round(endpoint[1])), (198, 83))

    def test_law_of_sines(self):
        angle = tri.law_of_sines(200, 200, 200)
        self.assertEqual(round(angle), 60)

        angle = tri.law_of_sines(200, 200, math.sqrt(200**2 + 200**2))
        self.assertEqual(round(angle), 90)

        angle = tri.law_of_sines(371, 353, 160)
        self.assertEqual(round(angle), 25)

        angle = tri.law_of_sines(371, 160, 353)
        self.assertEqual(round(angle), 71)

    def test_law_of_cosines(self):
        length = tri.law_of_cosines(200, 200, 60)
        self.assertEqual(round(length), 200)

        length = tri.law_of_cosines(371, 371, 140)
        self.assertEqual(round(length), 697)

    def test_line_distance(self):
        length = tri.line_distance((0, 10), (0, 0))
        self.assertEqual(round(length), 10)

        length = tri.line_distance((0, 10), (-20, 10))
        self.assertEqual(round(length), 20)

        length = tri.line_distance((0, 0), (10, 10))
        self.assertEqual(round(length), 14)

    def test_line_angle(self):
        angle = tri.line_angle((10, 0), (0, 0))
        self.assertEqual(round(angle), 0)

        angle = tri.line_angle((0, 0), (10, 0))
        self.assertEqual(round(angle), 180)

        angle = tri.line_angle((0, 10), (0, 0))
        self.assertEqual(round(angle), 90)

        angle = tri.line_angle((0, 0), (0, 10))
        self.assertEqual(round(angle), 270)

        angle = tri.line_angle((10, 10), (0, 0))
        self.assertEqual(round(angle), 45)

        angle = tri.line_angle((0, 0), (10, 10))
        self.assertEqual(round(angle), 225)

if __name__ == '__main__':
    unittest.main()
