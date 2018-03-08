''' ANN MODULE '''
import numpy as np

__author__ = 'Olve Drageset, Andre Gramlich'

def flatten_weights(list_of_mats):
    flat_ndlist = []
    for arr in list_of_mats:
        flat_ndlist.append(arr.flatten().tolist())
    flat_list = [item for sublist in flat_ndlist for item in sublist]
    return flat_list

class NeuralNet:
    def __init__(self, weights, nr_of_input_nodes=12, hidden_layers=1,
                 hidden_layer_nodes=6, nr_of_outputs=2, recurrence=False):
        self.nr_of_input_nodes = nr_of_input_nodes
        self.hidden_layers = hidden_layers
        self.hidden_layer_nodes = hidden_layer_nodes
        self.nr_of_output_nodes = nr_of_outputs
        self.weights = weights  # One array of numbers, that contain the weights ordered
        self.recurrence = recurrence
        if recurrence:
            self.prev_out = []
            self.nr_of_input_nodes += nr_of_outputs
            for i in range(0, nr_of_outputs):
                self.prev_out.append(0)

    def weights_as_mat(self):
        weights = []
        split_count = self.nr_of_output_nodes
        # Initialize matrix from input layer to first layer
        if self.hidden_layers > 0:
            w1 = np.empty([self.nr_of_input_nodes, self.hidden_layer_nodes])
            split_count = self.hidden_layer_nodes
        else:  # If first layer is output layer
            w1 = np.empty([self.nr_of_input_nodes, self.nr_of_output_nodes])
        start = 0
        for index, vector in enumerate(w1):
            w1[index] = self.weights[start:start + split_count]
            start += split_count
        weights.append(w1)

        if self.hidden_layers > 0:
            # Matrices between hidden layers
            for i in range(1, self.hidden_layers):
                wi = np.empty([self.hidden_layer_nodes, self.hidden_layer_nodes])
                for index, vector in enumerate(wi):
                    wi[index] = self.weights[start:start + self.hidden_layer_nodes]
                    start += self.hidden_layer_nodes
                weights.append(wi)

            # Matrix from last hidden layer to output layer
            wn = np.empty([self.hidden_layer_nodes, self.nr_of_output_nodes])
            for index, vector in enumerate(wn):
                wn[index] = self.weights[start:start + self.nr_of_output_nodes]
                start += self.nr_of_output_nodes
            weights.append(wn)
        return weights

    def forward_prop(self, _inputs):
        """
            Append last rounds outputs as input values if recurrence is enabled
        """

        inputs = list(_inputs)
        if self.recurrence:
            for out in self.prev_out:
                inputs.append(out)
        output = inputs  # The inputs will be transformed to output through several matmuls
        # This is where we propagate through the layers
        for weights in self.weights_as_mat():
            output = np.tanh(np.matmul(output, weights))
        self.prev_out = output  # Store for future recurrence use
        return output

    def get_velocities(self, inputs):
        """
            The inputs are in format [sensor_value1, sensor_value2, ..., sensor_valueN]
            The output is expected to be in format [left_velocity, right_velocity]
        """

        return self.forward_prop(inputs)