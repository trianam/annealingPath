import numpy as np

class Oven:
    def __init__(self, initialTemperature=1000, warmingRatio=0.8, trials=100, minTemperature=1, minDeltaEnergy=10):
        self._initialTemperature = initialTemperature
        self._warmingRatio = warmingRatio
        self._trials = trials
        self._minTemperature = minTemperature
        self._minDeltaEnergy = minDeltaEnergy

    def anneal(self, path):
        """
        Run the simulated annealing process. Start from given initial
        temperature and start a loop. In each iteration make a certain
        amount of statistic moves (trial), then decrease the
        temperature by a certain factor and then continue to next
        iteration. The loop ends when a certain minimal temperature is
        reached, or when the difference between the energy of the
        initial configuration and the final configuration, is less
        than a certain treshold.
        """
        temperature = self._initialTemperature
        while True:
            initialEnergy = path.energy()
            for i in range(self._trials):
                path.tryMove(temperature)

            finalEnergy = path.energy()
            temperature = temperature * self._warmingRatio
            if (temperature < self._minTemperature) or (abs(initialEnergy - finalEnergy) < self._minDeltaEnergy):
                break
