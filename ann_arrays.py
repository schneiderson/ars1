import numpy as np
import random

__author__ = 'Olve Drageset, Andre Gramlich'


def gen_nn(weights, inputs=14, hidden_layers=1, hidden_layer_nodes=6, outputs=2, init_range=[-1, 1]):
    weights = []
    num_of_weights = 0
    if hidden_layers > 0:
        num_of_weights += inputs * hidden_layer_nodes  # Links from input to first hidden
        num_of_weights += hidden_layer_nodes * outputs  # Links from last hidden to out
    if hidden_layers > 1:
        num_of_weights += hidden_layer_nodes ** hidden_layers  # Links between hidden layers
    else:
        num_of_weights += inputs * outputs  # Links from input to output layer

    for i in range(0, num_of_weights):
        weights.append(random.uniform(init_range[0], init_range[1]))


def flatten_weights(list_of_mats):
    flat_ndlist = []
    for arr in list_of_mats:
        flat_ndlist.append(arr.flatten().tolist())
    flat_list = [item for sublist in flat_ndlist for item in sublist]
    return flat_list


class NeuralNet:
    def __init__(self, weights, nr_of_input_nodes=12, hidden_layers=1, hidden_layer_nodes=6, nr_of_outputs=2, recurrence=False):
        self.nr_of_input_nodes = nr_of_input_nodes
        self.hidden_layers = hidden_layers
        self.hidden_layer_nodes = hidden_layer_nodes
        self.nr_of_outputs = nr_of_outputs
        self.weights = weights  # One array of numbers, that contain the weights ordered
        self.recurrence = recurrence
        if recurrence:
            self.prev_out = []
            self.nr_of_input_nodes += nr_of_outputs
            for i in range(0, nr_of_outputs):
                self.prev_out.append(0)

    def weights_as_mat(self):

        weights = []

        if self.hidden_layers > 0:
            w1 = np.empty([self.hidden_layer_nodes, self.nr_of_input_nodes])
        else:
            w1 = np.empty([self.nr_of_outputs, self.nr_of_input_nodes])
        start = 0
        for index, vector in enumerate(w1):
            w1[index] = self.weights[start:start + self.nr_of_input_nodes]
            start += self.nr_of_input_nodes
        weights.append(w1)

        if self.hidden_layers > 0:
            for i in range(1, self.hidden_layers):
                wi = np.empty([self.hidden_layer_nodes, self.hidden_layer_nodes])
                for index, vector in enumerate(wi):
                    wi[index] = self.weights[start:start + self.hidden_layer_nodes]
                    start += self.hidden_layer_nodes
                weights.append(wi)

            wL = np.empty([self.hidden_layer_nodes, self.nr_of_outputs])
            for index, vector in enumerate(wL):
                wL[index] = self.weights[start:start + self.hidden_layer_nodes]
                start += self.hidden_layer_nodes
            weights.append(wL)
        return weights

    def forward_prop_init(self, inputs):
        print(f"INPUT:{inputs}")
        if self.recurrence:
            for out in self.prev_out:
                inputs.append(out)
        print(f"INPUTS AFTER RECURRENCE APPENDED:{inputs}")

        weights_mats = self.weights_as_mat()
        output = inputs
        for weights in weights_mats:
            print(f"WEIGHTS: {weights}")
            # output = np.tanh(np.matmul(output, weights))
            output = np.matmul(output, weights)
            print(f"OUTPUTS:{output}")
        self.prev_out = output
        return output

    def forward_prop(self, input_values, weights_mat):
        H = np.matmul(input_values, weights_mat[0])
        H = np.tanh(H)
        return H
