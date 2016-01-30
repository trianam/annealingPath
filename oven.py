import numpy as np

class Oven:
    def __init__(self, initialTemperature=100000000, warmingRatio=0.8, trials=100, minTemperature=0.000001, minDeltaEnergy=0.000001):
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
            print('t:{0:<22};e:{1:<22};l:{2:<22};a:{3:<22};c:{4:<22};l:{5:<22}'.format(temperature, path.energy, path.length, path.meanAngle, path.costraints, path.vlambda))
            initialEnergy = path.energy
            for i in range(self._trials):
                path.tryMove(temperature)
            finalEnergy = path.energy
            temperature = temperature * self._warmingRatio
            if (temperature < self._minTemperature) or (abs(initialEnergy - finalEnergy) < self._minDeltaEnergy):
                break
