import numpy as np

class Oven:
    def __init__(self, initialPath=np.array([])):
        self._initialPath = initialPath

    def annealing(self, initialTemperature=1000, warmingRatio=0.8, trials=100):
        pass
