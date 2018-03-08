''' ANN MODULE '''
import ann_arrays as nn

__author__ = 'Olve Drageset'


class ANN:
    def __init__(self, weights):
        # The weights are coming straight from the argument that was passed to environment.simulate()
        self.ann = nn.NeuralNet(weights=weights)

    def get_velocities(self, inputs):
        # The inputs are in format [sensor_value1, sensor_value2, ..., sensor_valueN]
        # The output is expected to be in format [left_velocity, right_velocity]
        return self.ann.forward_prop(inputs)
