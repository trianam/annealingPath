import smoothener
import random
import math
import numpy as np

class Path:
    _angleSlices = 10
    _distanceStep = 1
    def __init__(self, initialVertexes):
        self._smoothener = smoothener.Smoothener()
        self._vertexes = initialVertexes
        self._currentEnergy = self._calculatePathEnergy(initialVertexes)

    def energy(self):
        return self._currentEnergy
    
    def tryMove(self, temperature):
        """
        Move the path in a neighbouring state, with a certain
        acceptance probability.
        Pick a random vertex (except extremes), and move
        it in a random direction (discretized with a certain treshold)
        by a distance step.
        """
        newPath = np.copy(self._vertexes)
        moveIndex = random.randint(1,len(newPath-2))
        moveAngle = random.randint(0,self._angleSlices-1)*math.pi/self._angleSlices

        newPath[moveIndex][0] = newPath[moveIndex][0] + math.cos(moveAngle) * self._distanceStep
        newPath[moveIndex][1] = newPath[moveIndex][1] + math.sin(moveAngle) * self._distanceStep

        newEnergy = self._calculatePathEnergy(newPath)
        if (newEnergy < self._currentEnergy) or (math.exp(-(newEnergy-self._currentEnergy)/temperature) >= random.random()):
            self._vertexes = newPath
            self._currentEnergy = newEnergy
        
    def _calculatePathEnergy(self, vertexes):
        """
        calculate the energy of the passed path and returns it. Use a
        lagrangian relaxation because we neet to evaluate
        min(len(path)) given the costraint that all quadrilaters
        formed by 4 consecutive points in the path must be collision
        free.
        """
        return 0
        
    def plot(self, plotter, plotStartEnd=True, plotInnerVertexes=False, plotEdges=True, plotSpline=True):
        if self._vertexes.size > 0:
            self._smoothener.plot(self._vertexes, plotter, plotStartEnd, plotInnerVertexes, plotEdges, plotSpline)
