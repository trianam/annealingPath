import numpy as np
import matplotlib.animation

class Oven:
    def __init__(self, initialTemperature=1000, warmingRatio=0.9, trials=100, minTemperature=0.00000001, minDeltaEnergy=0.000001):
        self._initialTemperature = initialTemperature
        self._warmingRatio = warmingRatio
        self._trials = trials
        self._minTemperature = minTemperature
        self._minDeltaEnergy = minDeltaEnergy

    def anneal(self, path, useLength=True, neighbourMode=0):
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
                path.tryMove(temperature, useLength, neighbourMode)
            finalEnergy = path.energy
            temperature = temperature * self._warmingRatio
            if (temperature < self._minTemperature) or (abs(initialEnergy - finalEnergy) < self._minDeltaEnergy):
                break

    def annealAnimation(self, path, figure, axes, useLength=True, neighbourMode=0):
        self._aniLine, = axes.plot([], [], 'ko-')
        self._aniSpline, = axes.plot([], [], 'r-', lw=2)
        self._textTemp = axes.text(0.02, 0.95, '', transform=axes.transAxes)
        self._textEner = axes.text(0.02, 0.90, '', transform=axes.transAxes)
        self._textLen = axes.text(0.02, 0.85, '', transform=axes.transAxes)
        self._textAng = axes.text(0.02, 0.80, '', transform=axes.transAxes)
        self._textCos = axes.text(0.02, 0.75, '', transform=axes.transAxes)
        self._textLam = axes.text(0.02, 0.70, '', transform=axes.transAxes)
        self._path = path
        self._temperature = self._initialTemperature
        ani = matplotlib.animation.FuncAnimation(figure, self._animate, interval=5, blit=True, repeat=False, fargs=(useLength,neighbourMode), init_func=self._init)

    def _init(self):
        self._aniLine.set_data([], [])
        self._aniSpline.set_data([], [])
        self._textTemp.set_text('')
        self._textEner.set_text('')
        self._textLen.set_text('')
        self._textAng.set_text('')
        self._textCos.set_text('')
        self._textLam.set_text('')
        
        return self._aniLine, self._aniSpline, self._textTemp, self._textEner, self._textLen, self._textAng, self._textCos, self._textLam
        
    def _animate(self, i, useLength, neighbourMode):
        for i in range(self._trials):
            self._path.tryMove(self._temperature, useLength, neighbourMode)

        self._aniLine.set_data(self._path.vertexes[:,0], self._path.vertexes[:,1])
        self._aniSpline.set_data(self._path.spline[:,0], self._path.spline[:,1])
        self._textTemp.set_text('temp.  = {}'.format(self._temperature))
        self._textEner.set_text('Energy = {}'.format(self._path.energy))
        self._textLen.set_text('Length = {}'.format(self._path.length))
        self._textAng.set_text('Angle  = {}'.format(self._path.meanAngle))
        self._textCos.set_text('Costr. = {}'.format(self._path.costraints))
        self._textLam.set_text('Lambda = {}'.format(self._path.vlambda))

        self._temperature = self._temperature * self._warmingRatio

        return self._aniLine, self._aniSpline, self._textTemp, self._textEner, self._textLen, self._textAng, self._textCos, self._textLam
