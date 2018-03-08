import unittest
import numpy as np
from bot import ann as nn
import numpy.testing as npt

__author__ = 'Olve Drageset, Andre Gramlich'


class TestANN(unittest.TestCase):
    def testTranslation(self):
        array = [0., 1., 2., 3., 4., 5., 6., 7.]
        mat1 = [np.array([[0., 1.], [2., 3.], [4., 5.], [6., 7.]])]

        net = nn.NeuralNet(weights=array, nr_of_input_nodes=4, hidden_layers=0, nr_of_outputs=2, recurrence=False)
        mat2 = net.weights_as_mat()
        for i in range(0, len(mat1)):
            npt.assert_almost_equal(mat1[i], mat2[i])

    def testTranslationWithHiddenLayer(self):
        array = [0., 1., 2., 3., 4., 5., 6., 7., 8., 9., 10., 11., 12., 13.]
        mat1 = [np.array([[0., 1.], [2., 3.], [4., 5.], [6., 7.]]), np.array([[8., 9., 10.], [11., 12., 13.]])]

        net = nn.NeuralNet(
            weights=array,
            nr_of_input_nodes=4,
            hidden_layers=1,
            hidden_layer_nodes=2,
            nr_of_outputs=3,
            recurrence=False)
        mat2 = net.weights_as_mat()
        for i in range(0, len(mat1)):
            npt.assert_almost_equal(mat1[i], mat2[i])

    def testTranslationWithRecurrence(self):
        array = [0., 1., 2., 3., 4., 5., 6., 7., 8., 9., 10., 11.]
        mat1 = [np.array([[0., 1.], [2., 3.], [4., 5.], [6., 7.]]), np.array([[8., 9.], [10., 11.]])]

        net = nn.NeuralNet(
            weights=array,
            nr_of_input_nodes=2,
            hidden_layers=1,
            hidden_layer_nodes=2,
            nr_of_outputs=2,
            recurrence=True)
        mat2 = net.weights_as_mat()
        for i in range(0, len(mat1)):
            npt.assert_almost_equal(mat1[i], mat2[i])

    def testFlatten(self):
        array = [0., 1., 2., 3., 4., 5., 6., 7., 8., 9., 10., 11.]
        mat1 = [np.array([[0., 1., 2., 3.], [4., 5., 6., 7.]]), np.array([[8., 9.], [10., 11.]])]
        flat_list = nn.flatten_weights(mat1)
        self.assertAlmostEqual(array, flat_list)

    def testForwardPropagation(self):
        inputs = [1., 1.]
        weights = [np.array([[1., 2.], [1., 2.]])]
        weights_flat = nn.flatten_weights(weights)
        expected_output = nn.flatten_weights(np.tanh([2., 4.]))
        net = nn.NeuralNet(weights=weights_flat,
                           nr_of_input_nodes=len(inputs),
                           hidden_layers=0,
                           hidden_layer_nodes=0,
                           nr_of_outputs=2,
                           recurrence=False)
        output = nn.flatten_weights(net.forward_prop(inputs))
        self.assertAlmostEqual(expected_output, output)

    def testForwardPropagationWithHiddenLayer(self):
        inputs = [1., 1.]
        weights = [np.array([[1., 2.], [1., 2.]]), np.array([[1., 1.], [1., 1.]])]
        expected_output = nn.flatten_weights(
            np.tanh([1.9633568798148839277386570684426, 1.9633568798148839277386570684426]))
        weights_flat = nn.flatten_weights(weights)
        net = nn.NeuralNet(weights=weights_flat,
                           nr_of_input_nodes=len(inputs),
                           hidden_layers=1,
                           hidden_layer_nodes=2,
                           nr_of_outputs=2,
                           recurrence=False)
        output = nn.flatten_weights(net.forward_prop(inputs))
        self.assertAlmostEqual(expected_output, output)

    def testForwardPropagationWithHiddenLayerAndRecurrence(self):
        inputs = [1., 1.]
        weights = [np.array([[1., 2.], [1., 2.], [1., 1.], [1., 1.]]), np.array([[1., 1.], [1., 1.]])]
        weights_flat = nn.flatten_weights(weights)
        net = nn.NeuralNet(weights=weights_flat,
                           nr_of_input_nodes=len(inputs),
                           hidden_layers=1,
                           hidden_layer_nodes=2,
                           nr_of_outputs=2,
                           recurrence=True)
        expected_output_iteration_1 = nn.flatten_weights(
            np.tanh([1.9633568798148839277386570684426, 1.9633568798148839277386570684426]))
        # on the first iteration the memory nodes are initialized with 0
        output_iteration_1 = nn.flatten_weights(net.forward_prop(inputs))
        self.assertAlmostEqual(expected_output_iteration_1, output_iteration_1)

        # on the second round the memory nodes the value from the previous iteration
        expected_output_iteration_2 = nn.flatten_weights(
            np.tanh([1.99920285031581971304150882377, 1.99920285031581971304150882377]))
        output_iteration_2 = nn.flatten_weights(net.forward_prop(inputs))
        print(expected_output_iteration_2)
        print(output_iteration_2)
        self.assertAlmostEqual(expected_output_iteration_2, output_iteration_2)
