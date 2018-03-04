import math
import numpy as np


# Rosenbrock benchmarking function for two dimensions
def rosenbrock(x, y):
    return int((1 - x) ** 2 + 100 * (y - x ** 2) ** 2)


# Rastrigin benchmarking function for n dimensions
def rastrigin(*x, **kwargs):
    a = kwargs.get('A', 10)
    return a + sum([(x**2 - a * np.cos(2 * math.pi * x)) for x in x])


# The cost function from Rico's Machine Learning homework
def testfunc(x, y):
    xvector = [0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5]
    yvector = [0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5]
    m = len(xvector)
    h0 = x + np.dot(xvector, y)
    return 1/(2*m) * sum((h0-yvector)**2)

