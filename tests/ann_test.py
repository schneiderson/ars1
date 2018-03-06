import unittest
import numpy as np
import ann_arrays as nn
import numpy.testing as npt


class TestANN(unittest.TestCase):
    def testTranslation(self):
        array = [0., 1., 2., 3., 4., 5., 6., 7.]
        mat1 = [np.array([[0., 1., 2., 3.], [4., 5., 6., 7.]])]

        net = nn.NeuralNet(weights=array, nr_of_input_nodes=4, hidden_layers=0, nr_of_outputs=2)
        mat2 = net.weights_as_mat()
        print(mat1)
        print(mat2)
        for i in range(0, len(mat1)):
            npt.assert_almost_equal(mat1[i], mat2[i])

    def testTranslation2(self):
        array = [0., 1., 2., 3., 4., 5., 6., 7., 8., 9., 10., 11.]
        mat1 = [np.array([[0., 1., 2., 3.], [4., 5., 6., 7.]]), np.array([[8., 9.], [10., 11.]])]

        net = nn.NeuralNet(weights=array, nr_of_input_nodes=4, hidden_layers=1, hidden_layer_nodes=2, nr_of_outputs=2)
        mat2 = net.weights_as_mat()
        print(mat1)
        print(mat2)
        for i in range(0, len(mat1)):
            npt.assert_almost_equal(mat1[i], mat2[i])

    def testFlatten(self):
        array = [0., 1., 2., 3., 4., 5., 6., 7., 8., 9., 10., 11.]
        mat1 = [np.array([[0., 1., 2., 3.], [4., 5., 6., 7.]]), np.array([[8., 9.], [10., 11.]])]
        flat_list = nn.flatten_weights(mat1)
        print("FLAT:")
        print(flat_list)
        self.assertAlmostEqual(array, flat_list)
