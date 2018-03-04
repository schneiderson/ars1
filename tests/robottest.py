import unittest
import math
from bot import robot as bot

__author__ = 'Camiel Kerkhofs'

ROBOT = bot.Robot()

class TestRobot(unittest.TestCase):

    def test_line_intersection(self):
        tmp = ROBOT.find_line_intersect((10,10),(20,10),(10,20),(20,20))
        self.assertEqual(tmp, False)
        
        tmp = ROBOT.find_line_intersect((10,10),(20,20),(50,5),(20,18))
        self.assertEqual(tmp, False)
        
        tmp = ROBOT.find_line_intersect((10,10),(20,20),(10,8),(20,22))
        self.assertEqual(tmp, (15, 15))
        
        tmp = ROBOT.find_line_intersect((10,10),(20,30),(10,0),(20,40))
        self.assertEqual(tmp, (15, 20))

    def test_sensors_update(self):
        walls = [
            [(50, 50), (750, 50)],
            [(50, 750), (750, 750)],
            [(50, 50), (50, 750)],
            [(750, 50), (750, 750)],
        ]
        
        # Robot faces top
        ROBOT.set_robot_position(100, 100, 270)
        ROBOT.update_sensors(walls)
        output = ROBOT.sensors
        self.assertAlmostEqual(round(output[0][0]), 50)
        self.assertAlmostEqual(round(output[1][0]), 58)
        self.assertAlmostEqual(round(output[2][0]), 100)
        self.assertAlmostEqual(round(output[3][0]), 500)
        self.assertAlmostEqual(round(output[4][0]), 500)
        
        # Robot faces right
        ROBOT.set_robot_position(100, 100, 0)
        ROBOT.update_sensors(walls)
        output = ROBOT.sensors
        self.assertAlmostEqual(round(output[0][0]), 500)
        self.assertAlmostEqual(round(output[1][0]), 500)
        self.assertAlmostEqual(round(output[3][0]), 500)
        self.assertAlmostEqual(round(output[6][0]), 50)
        self.assertAlmostEqual(round(output[9][0]), 50)
        
 
if __name__ == '__main__':
    unittest.main()
