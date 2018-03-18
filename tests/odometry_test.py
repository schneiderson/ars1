import unittest
import math
from bot import odometry as od

__author__ = 'Steffen Schneider'

class TestOdometry(unittest.TestCase):

    def test_normal_dist(self):
        tmp = od.prob_normal_dist(0, 1)
        self.assertEqual(round(tmp, 10), 0.3989422804)

        tmp = od.prob_normal_dist(1, 1)
        self.assertEqual(round(tmp, 10), 0.2419707245)

        tmp = od.prob_normal_dist(-1, 1)
        self.assertEqual(round(tmp, 10), 0.2419707245)

        tmp = od.prob_normal_dist(3, 1)
        self.assertEqual(round(tmp, 10), 0.0044318484)

        tmp = od.prob_normal_dist(6, 1)
        self.assertEqual(round(tmp, 10), 0.0000000061)

        tmp = od.prob_normal_dist(5, 5)
        self.assertEqual(round(tmp, 10), 0.0483941449)


    def test_traing_dist(self):
        tmp = od.prob_triang_dist(0, 1)
        self.assertEqual(round(tmp, 10), 0.4082482905)

        tmp = od.prob_triang_dist(1, 1)
        self.assertEqual(round(tmp, 10), 0.2415816238)

        tmp = od.prob_triang_dist(-1, 1)
        self.assertEqual(round(tmp, 10), 0.2415816238)

        tmp = od.prob_triang_dist(3, 1)
        self.assertEqual(tmp, 0)

        tmp = od.prob_triang_dist(5, 5)
        self.assertEqual(round(tmp, 10), 0.0483163248)
        
        

    def test_atan2(self):
        tmp = od.atan2(0, 0)
        self.assertEqual(tmp, 0)

        tmp = od.atan2(1, 1)
        self.assertEqual(round(tmp, 10), 0.7853981634)

        tmp = od.atan2(1, -1)
        self.assertEqual(round(tmp, 10), 2.3561944902)

        tmp = od.atan2(-1, 1)
        self.assertEqual(round(tmp, 10), -0.7853981634)

        tmp = od.atan2(-1, -1)
        self.assertEqual(round(tmp, 10), -2.3561944902)

        tmp = od.atan2(1, 0)
        self.assertEqual(round(tmp, 10), 1.5707963268)

        tmp = od.atan2(0, 1)
        self.assertEqual(tmp, 0)

        tmp = od.atan2(-1, 0)
        self.assertEqual(round(tmp, 10), -1.5707963268)

        tmp = od.atan2(0, -1)
        self.assertEqual(round(tmp, 10), 3.1415926536)


    def test_delta_trans(self):
        tmp = od.delta_trans(1, 1, 1, 1)
        self.assertEqual(tmp, 0)

        tmp = od.delta_trans(1, 1, 1, 3)
        self.assertEqual(tmp, 2)

        tmp = od.delta_trans(1, 1, 2, 2)
        self.assertEqual(round(tmp, 10), 1.4142135624)

        tmp = od.delta_trans(1, 1, -1, -1)
        self.assertEqual(round(tmp, 10), 2.8284271247)
         

    def test_probabilities(self):
        odometry = od.odometry()

        pos_t0 = (0, 0, 0)          # current position
        pos_t1 = (1, 0, 0)          # position after move
        u_t = [(0, 0, 0), (1, 0, 0)] # measured positions before and after move (from encoder data)
        # get probability
        prob = odometry.get_prob(pos_t0, pos_t1, u_t)
        self.assertEqual(round(prob, 10), 63.4936359342)
        
        # set another prob func
        odometry.set_prob_func(od.prob_triang_dist)
        # get probability
        prob = odometry.get_prob(pos_t0, pos_t1, u_t)
        self.assertEqual(round(prob, 10), 68.0413817440)


    def test_sampling(self):
        odometry = od.odometry()

        pos_t0 = (0, 0, 0)          # current position
        u_t = [(0, 0, 0), (1, 0, 0)] # measured positions before and after move (from encoder data)
        # get probability
        pose = odometry.sample_motion_model(u_t, pos_t0)
        self.assertTrue( math.fabs(pose[0] - u_t[1][0]) < .4 )
        self.assertTrue( math.fabs(pose[1]) < .4 )
        self.assertTrue( math.fabs(pose[2]) < 30 )
        
        # set another prob func
        odometry.set_prob_func(od.prob_triang_dist)
        # get probability
        pose = odometry.sample_motion_model(u_t, pos_t0)
        print(pose)
        self.assertTrue( math.fabs(pose[0] - u_t[1][0]) < .4 )
        self.assertTrue( math.fabs(pose[1]) < .4 )
        self.assertTrue( math.fabs(pose[2]) < 30 )


if __name__ == '__main__':
    unittest.main()
