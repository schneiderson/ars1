import numpy as np
import random
import math


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


class NeuralNet:

    def __init__(self, weights, inputs=14, hidden_layers=1, hidden_layer_nodes=6, outputs=2):
        self.inputs = inputs
        self.hidden_layers = hidden_layers
        self.hidden_layer_nodes = hidden_layer_nodes
        self.outputs = outputs
        self.weights = weights

    def forward_prop(self, inputs):

        W1 = [] * self.hidden_layer_nodes
        W1 = np.matri



        H = np.matmul(inputs, W1)
        H = np.tanh(H)
        O = np.matmul(H, W2)
        O = np.tanh(O)
        return O



