import numpy as np

class Oven:
    def __init__(self, path):
        self._path = path

    def annealing(self, initialTemperature=1000, warmingRatio=0.8, trials=100, minTemperature=1, minDeltaEnergy=10):
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
        temperature = initialTemperature
        while true:
            initialEnergy = self._path.energy()
            for i in range(trials):
                self._path.tryMove(temperature)

            finalEnergy = self._path.energy()
            temperature = temperature * warmingRatio
            if (temperature < minTemperature) or (abs(initialEnergy - finalEnergy) < minDeltaEnergy):
                break
