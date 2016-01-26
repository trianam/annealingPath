import smoothener
import random
import math
import numpy as np

class Path:
    """
    Represents a state of system in the lagrangian space (path
    configurations X costraint).
    """
    _maxVlambdaPert = 1.
    _maxVertexPert = 1.
    _initialVlambda = 0.
    _changeVlambdaProbability = 0.05
    
    def __init__(self, initialVertexes):
        self._smoothener = smoothener.Smoothener()
        self._vertexes = initialVertexes
        self._dimR = self._vertexes.shape[0]
        self._dimC = self._vertexes.shape[1]
        self._vlambda = np.ones(self._vertexes.shape) * self._initialVlambda 
        self._currentEnergy = self._calculatePathEnergy(self._vertexes, self._vlambda)

    def energy(self):
        return self._currentEnergy
    
    def tryMove(self, temperature):
        """
        Move the path or lambda multipiers in a neighbouring state,
        with a certain acceptance probability.
        Pick a random vertex (except extremes), and move
        it in a random direction (with a maximum perturbance).
        """

        moveR = random.randint(1,self._dimR - 2) #don't change extremes
        moveC = random.randint(0,self._dimC - 1)

        if random.random() < self._changeVlambdaProbability:
            newVlambda = np.copy(self.vlambda)
            newVlambda[moveR][moveC] = newVlambda[moveR][moveC] + (random.uniform(-1.,1.) * self._maxVlambdaPert)

            newEnergy = self._calculatePathEnergy(self._vertexes, newVlambda)

            #attention, different formula
            if (newEnergy > self._currentEnergy) or (math.exp(-(self._currentEnergy-newEnergy)/temperature) >= random.random()):
                self._vlambda = newVlambda
                self._currentEnergy = newEnergy
        
        else:
            newVertexes = np.copy(self._vertexes)
            newVertexes[moveR][moveC] = newVertexes[moveR][moveC] + (random.uniform(-1.,1.) * self._maxVertexPert)

            newEnergy = self._calculatePathEnergy(newVertexes, self._vlambda)

            #attention, different formula
            if (newEnergy < self._currentEnergy) or (math.exp(-(newEnergy-self._currentEnergy)/temperature) >= random.random()):
                self._vertexes = newVertexes
                self._currentEnergy = newEnergy
        
    def _calculatePathEnergy(self, vertexes, vlambda):
        """
        calculate the energy of the passed path and returns it. Use a
        lagrangian relaxation because we need to evaluate
        min(meanAngle(path)) given the costraint that all quadrilaters
        formed by 4 consecutive points in the path must be collision
        free; where meanAngle(path) is the mean of the supplementary
        angles of each pair of edges of the path.
        """

        
        return 0
        
    def plot(self, plotter, plotStartEnd=True, plotInnerVertexes=False, plotEdges=True, plotSpline=True):
        if self._vertexes.size > 0:
            self._smoothener.plot(self._vertexes, plotter, plotStartEnd, plotInnerVertexes, plotEdges, plotSpline)
