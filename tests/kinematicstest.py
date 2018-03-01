import unittest
import math
from bot import kinematics as kin

class TestKinematics(unittest.TestCase):

    def test_total_velocity(self):
        tmp = kin.total_velocity(1, 1)
        self.assertEqual(tmp, 1)
        
        tmp = kin.total_velocity(0, 0)
        self.assertEqual(tmp, 0)
        
        tmp = kin.total_velocity(-1, 1)
        self.assertEqual(tmp, 0)
        
        tmp = kin.total_velocity(-1, -1)
        self.assertEqual(tmp, -1)


    def test_rotation_rate_by_velocities(self):
        # same velocity -> no rotation
        tmp = kin.rotation_rate_by_velocities(1, 1)
        self.assertEqual(tmp, 0)

        tmp = kin.rotation_rate_by_velocities(-1, -1)
        self.assertEqual(tmp, 0)
        
        # left > right -> clockwise rotation -> negative rate
        tmp = kin.rotation_rate_by_velocities(1, -1)
        self.assertEqual(tmp, -2)

        tmp = kin.rotation_rate_by_velocities(1, 0)
        self.assertEqual(tmp, -1)
        
        # left < right -> counter-clockwise rotation -> positive rate
        tmp = kin.rotation_rate_by_velocities(-1, 1)
        self.assertEqual(tmp, 2)
        
        tmp = kin.rotation_rate_by_velocities(0, 1)
        self.assertEqual(tmp, 1)



    def test_ICC_dist(self):
        # same velocities -> infinity
        tmp = kin.ICC_dist(1, 1)
        self.assertEqual(tmp, math.inf)

        tmp = kin.ICC_dist(-1, -1)
        self.assertEqual(tmp, math.inf)

        # different velocities
        tmp = kin.ICC_dist(0, 1)
        self.assertEqual(tmp, 0.5)

        tmp = kin.ICC_dist(1, 0)
        self.assertEqual(tmp, -0.5)


    def test_ICC_coordinates(self):
        # same velocity -> no rotation -> no ICC
        x, y = kin.ICC_coordinates(0, 0, 0, 0, 0)
        self.assertEqual((x, y), (None, None))

        x, y = kin.ICC_coordinates(0,0, 0, 1, 0, 2)
        self.assertEqual((round(x), round(y)), (0, -1))

        x, y = kin.ICC_coordinates(0,0, 90, 1, 0, 2)
        self.assertEqual((round(x), round(y)), (1, 0))

        x, y = kin.ICC_coordinates(0,0, 180, 1, 0, 2)
        self.assertEqual((round(x), round(y)), (0, 1))
        
        x, y = kin.ICC_coordinates(0,0, 270, 1, 0, 2)
        self.assertEqual((round(x), round(y)), (-1, 0))
        
        x, y = kin.ICC_coordinates(0,0, 360, 1, 0, 2)
        self.assertEqual((round(x), round(y)), (0, -1))
        
        x, y = kin.ICC_coordinates(0,0, 0, 0, 1, 2)
        self.assertEqual((round(x), round(y)), (0, 1))
        
        x, y = kin.ICC_coordinates(0,0, 90, 0, 1, 2)
        self.assertEqual((round(x), round(y)), (-1, 0))
        
        x, y = kin.ICC_coordinates(0,0, 180, 0, 1, 2)
        self.assertEqual((round(x), round(y)), (0, -1))
        
        x, y = kin.ICC_coordinates(0,0, 270, 0, 1, 2)
        self.assertEqual((round(x), round(y)), (1, 0))
        
        x, y = kin.ICC_coordinates(0,0, 360, 0, 1, 2)
        self.assertEqual((round(x), round(y)), (0, 1))


    def test_bot_calc_coordinate(self):
        # straight (movement to the right)
        x, y, d = kin.bot_calc_coordinate(0, 0, 0, 1, 1, 1, 2)
        self.assertEqual((round(x), round(y)), (1, 0))
        self.assertEqual(d, 0)

        # straight (movement to the left)
        x, y, d = kin.bot_calc_coordinate(0, 0, 0, -1, -1, 1, 2)
        self.assertEqual((round(x), round(y)), (-1, 0))
        self.assertEqual(d, 0)

        # straight (movement up)
        x, y, d = kin.bot_calc_coordinate(0, 0, 90, 1, 1, 1, 2)
        self.assertEqual((round(x), round(y)), (0, 1))
        self.assertEqual(d, 90)

        # straight (movement down)
        x, y, d = kin.bot_calc_coordinate(0, 0, 90, -1, -1, 1, 2)
        self.assertEqual((round(x), round(y)), (0, -1))
        self.assertEqual(d, 90)

        # quater turn (own axis)
        x, y, d = kin.bot_calc_coordinate(0, 0, 0, -0.25, 0.25, 1, 2)
        self.assertEqual((round(x), round(y)), (0, 0))
        self.assertEqual(d, 90)

        # half turn (own axis)
        x, y, d = kin.bot_calc_coordinate(0, 0, 0, -0.5, 0.5, 1, 2)
        self.assertEqual((round(x), round(y)), (0, 0))
        self.assertEqual(d, 180)

        # full turn (own axis)
        x, y, d = kin.bot_calc_coordinate(0, 0, 0, -1, 1, 1, 2)
        self.assertEqual((round(x), round(y)), (0, 0))
        self.assertEqual(d, 0)

        # streched curve
        x, y, d = kin.bot_calc_coordinate(0, 0, 0, 1, 2, 1, 4)
        self.assertEqual((round(x), round(y)), (6, 6))
        self.assertEqual(d, 90)

 
if __name__ == '__main__':
    unittest.main()
