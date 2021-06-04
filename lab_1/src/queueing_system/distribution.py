from numpy import random as nr
from . import exceptions as ex


class Uniform:
    def __init__(self, a, b):
        if not 0 <= a <= b:
            raise ex.ParameterError("Parameters must be 0 <= a <= b")
        self._a = a
        self._b = b

    def generate(self):
        return nr.uniform(self._a, self._b)

class Weibull:
    def __init__(self, a, lamb):
        self._a = a
        self._lamb = lamb

    def generate(self):
        return self._lamb*nr.weibull(self._a)

class Normal:
    def __init__(self, mu, sigma):
        self._mu = mu
        self._sigma = sigma

    def generate(self):
        return nr.normal(self._mu, self._sigma)
