''' ODOMETRY MODULE '''
import math
import random
import numpy

__author__ = 'Steffen Schneider'


class odometry:
    def __init__(self, noise_parameters=None):
        # self.np: alpha 1-4 (error/noise parameters)
        self.np = [.001, .001, .001, .001]
        if noise_parameters:
            self.np = noise_parameters

        self.prob_func = prob_normal_dist
        self.sample_func = sample_normal_dist

    def set_noise_params(self, noise_parameters):
        self.np = noise_parameters

    def set_prob_func(self, func):
        self.prob_func = func

    def set_sample_func(self, func):
        self.sample_func = func

    def get_prob(self, p1, p2, ut):

        # Measured odometry motion components
        d_trans = delta_trans(ut[0][0], ut[0][1], ut[1][0], ut[1][1])
        d_rot1 = delta_rot1(ut[0][0], ut[0][1], ut[1][0], ut[1][1], math.radians(ut[0][2]))
        d_rot2 = math.radians(ut[1][2]) - math.radians(ut[0][2]) - d_rot1

        # state to be evaluated
        d_hat_trans = delta_trans(p1[0], p1[1], p2[0], p2[1])
        d_hat_rot1 = delta_rot1(p1[0], p1[1], p2[0], p2[1], math.radians(p2[2]))
        d_hat_rot2 = math.radians(p2[2]) - math.radians(p1[2]) - d_hat_rot1

        # compute probabilities
        sd_p1 = self.np[0] * math.fabs(d_hat_rot1) + self.np[1] * d_hat_trans                           # standard deviation
        p_1 = self.prob_func(d_rot1 - d_hat_rot1, sd_p1)

        sd_p2 = self.np[2] * d_hat_trans + self.np[3] * (math.fabs(d_hat_rot1) + math.fabs(d_hat_rot2)) # standard deviation
        p_2 = self.prob_func(d_trans - d_hat_trans, sd_p2)

        sd_p3 = self.np[0] * math.fabs(d_hat_rot2) + self.np[1] * d_hat_trans                           # standard deviation
        p_3 = self.prob_func(d_rot2 - d_hat_rot2, sd_p3)

        return p_1 * p_2 * p_3


    def sample_motion_model(self, ut, pos):

        # Measured odometry motion components
        d_trans = delta_trans(ut[0][0], ut[0][1], ut[1][0], ut[1][1])
        d_rot1 = delta_rot1(ut[0][0], ut[0][1], ut[1][0], ut[1][1], math.radians(ut[0][2]))
        d_rot2 = math.radians(ut[1][2]) - math.radians(ut[0][2]) - d_rot1

        # Sample
        sd_p1 = self.np[0] * math.fabs(d_rot1) + self.np[1] * d_trans                       # standard deviation
        d_hat_rot1 = d_rot1 + self.sample_func(sd_p1)

        sd_p2 = self.np[2] * d_trans + self.np[3] * (math.fabs(d_rot1) + math.fabs(d_rot2)) # standard deviation
        d_hat_trans = d_trans + self.sample_func(sd_p2)

        sd_p3 = self.np[0] * math.fabs(d_rot2) + self.np[1] * d_trans                       # standard deviation
        d_hat_rot2 = d_rot2 + self.sample_func(sd_p3)

        # calculate new position
        x_prime = pos[0] + d_hat_trans * math.cos(math.radians(pos[2]) + d_hat_rot1)
        y_prime = pos[1] + d_hat_trans * math.sin(math.radians(pos[2]) + d_hat_rot1)
        angle_prime = math.radians(pos[2]) + d_hat_rot1 + d_hat_rot2
        angle = math.degrees(angle_prime) % 360

        return (x_prime, y_prime, angle)


''' Helper function '''


def delta_trans(x1, y1, x2, y2):
    return math.sqrt(((x2 - x1) ** 2) + (y2 - y1) ** 2)


def delta_rot1(x1, y1, x2, y2, angle):
    # note: angle should be in radians
    return atan2(y2 - y1, x2 - x1) - angle


def atan2(dy, dx):
    if dx > 0:
        return math.atan(dy / dx)
    elif dx < 0:
        return math.copysign(1, dy) * (math.pi - math.atan(math.fabs(dy / dx)))
    elif dx == dy == 0:
        return 0
    else:
        return math.copysign(1, dy) * math.pi / 2


''' Probability distributions '''


def prob_normal_dist(a, b):
    # standard deviation cant be zero, otherwise we'll encounter division by zero
    if b == 0: b = numpy.finfo(float).eps

    var = float(b) ** 2
    denom = math.sqrt(2 * math.pi * var)
    num = math.exp(-(float(a) ** 2 / (2 * var)))
    return num/denom


def prob_triang_dist(a, b):
    # standard deviation cant be zero, otherwise we'll encounter division by zero
    if b == 0: b = numpy.finfo(float).eps

    tmp = (1 / (math.sqrt(6) * b)) - (math.fabs(a) / (6 * b ** 2))
    return max(0, tmp)


''' Sampling functions '''


def sample_normal_dist(b):
    return .5 * sum([random.uniform(-b, b) for _ in range(12)])


def sample_triang_dist(b):
    return math.sqrt(6) * .5 * (random.uniform(-b, b) + random.uniform(-b, b))
