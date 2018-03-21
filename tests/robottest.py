import unittest
import math
from bot import robot as bot

__author__ = 'Camiel Kerkhofs'

ROBOT = bot.Robot()

class TestRobot(unittest.TestCase):

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
