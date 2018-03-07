''' ANN MODULE '''
import ann_arrays as nn

__author__ = ''

class ANN:
    def __init__(self, weights):
        self.ann = nn.NeuralNet(weights=weights)
        #TODO: the weights are coming straight from the argument that was passed to environment.simulate()

    def get_velocities(self, inputs):
        return self.ann.forward_prop(inputs)
        #TODO: the inputs are in format [sensor_value1, sensor_value2, ..., sensor_valueN]
        #TODO: ANN magic
        #TODO: the output is expected to be in format [left_velocity, right_velocity]
