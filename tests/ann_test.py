import unittest
import numpy as np
import ann_arrays as nn
import numpy.testing as npt
import math

__author__ = 'Olve Drageset'


class TestANN(unittest.TestCase):
    def testTranslation(self):
        array = [0., 1., 2., 3., 4., 5., 6., 7.]
        mat1 = [np.array([[0., 1., 2., 3.], [4., 5., 6., 7.]])]

        net = nn.NeuralNet(weights=array, nr_of_input_nodes=4, hidden_layers=0, nr_of_outputs=2, recurrence=False)
        mat2 = net.weights_as_mat()
        for i in range(0, len(mat1)):
            npt.assert_almost_equal(mat1[i], mat2[i])

    def testTranslation2(self):
        array = [0., 1., 2., 3., 4., 5., 6., 7., 8., 9., 10., 11.]
        mat1 = [np.array([[0., 1., 2., 3.], [4., 5., 6., 7.]]), np.array([[8., 9.], [10., 11.]])]

        net = nn.NeuralNet(weights=array, nr_of_input_nodes=4, hidden_layers=1, hidden_layer_nodes=2, nr_of_outputs=2, recurrence=False)
        mat2 = net.weights_as_mat()
        for i in range(0, len(mat1)):
            npt.assert_almost_equal(mat1[i], mat2[i])

    def testFlatten(self):
        array = [0., 1., 2., 3., 4., 5., 6., 7., 8., 9., 10., 11.]
        mat1 = [np.array([[0., 1., 2., 3.], [4., 5., 6., 7.]]), np.array([[8., 9.], [10., 11.]])]
        flat_list = nn.flatten_weights(mat1)
        self.assertAlmostEqual(array, flat_list)

    def testFWDPROP(self):
        inputs = [1., 1.]
        nr_of_input_nodes = len(inputs)
        hidden_layers = 0
        hidden_layer_nodes = 0
        nr_of_outputs = 2
        weights = [np.array([[1., 2.], [1., 2.]])]
        weights_flat = nn.flatten_weights(weights)
        expected_output = nn.flatten_weights(np.tanh([2., 4.]))
        net = nn.NeuralNet(weights=weights_flat,
                           nr_of_input_nodes=nr_of_input_nodes,
                           hidden_layers=hidden_layers,
                           hidden_layer_nodes=hidden_layer_nodes,
                           nr_of_outputs=nr_of_outputs,
                           recurrence=False)
        output = nn.flatten_weights(net.forward_prop(inputs))
        self.assertAlmostEqual(expected_output, output)

