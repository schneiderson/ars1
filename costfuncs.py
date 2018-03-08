import math
import numpy as np
from bot import environment as env


def get_output_params(number_of_params, gene):
    out = []
    for i in range(0, number_of_params):
        section_length = int(len(gene) / number_of_params)
        out.append(sum(gene[i * section_length:(i + 1) * section_length]))
    return out


# Rosenbrock benchmarking function for two dimensions
def rosenbrock(gene):
    parameters = get_output_params(2, gene)
    return int((1 - parameters[0]) ** 2 + 100 * (parameters[1] - parameters[0] ** 2) ** 2)


# Rastrigin benchmarking function for n dimensions
def rastrigin(*x, **kwargs):
    a = kwargs.get('A', 10)
    return a * len(x) + sum([(x**2 - a * np.cos(2 * math.pi * x)) for x in x])


# The cost function from Rico's Machine Learning homework
def testfunc(gene):
    parameters = get_output_params(2, gene)
    xvector = [0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5]
    yvector = [0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5]
    m = len(xvector)
    h0 = parameters[0] + np.dot(xvector, parameters[1])
    return 1/(2*m) * sum((h0-yvector)**2)

