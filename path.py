import random
import math
import numpy as np
import scipy.interpolate as si

class Path:
    """
    Represents a state of system in the lagrangian space (path
    configurations X costraint).
    """
    _maxVlambdaPert = 10.
    _maxVertexPert = 0.01
    _initialVlambda = 0.
    _changeVlambdaProbability = 0.05
    _numPointsSplineMultiplier = 10
    
    def __init__(self, initialVertexes, scene):
        self._vertexes = initialVertexes
        self._scene = scene
        self._dimR = self._vertexes.shape[0]
        self._dimC = self._vertexes.shape[1]
        self._numPointsSpline = self._numPointsSplineMultiplier * self._dimR
        self._vlambda = self._initialVlambda 
        self._currentEnergy, self._currentLength, self._currentMeanAngle, self._currentCostraints = self._initializePathEnergy(self._vertexes, self._vlambda)

    @property
    def vertexes(self):
        return self._vertexes
    
    @property
    def energy(self):
        return self._currentEnergy
    
    @property
    def length(self):
        return self._currentLength
    
    @property
    def meanAngle(self):
        return self._currentMeanAngle
    
    @property
    def costraints(self):
        return self._currentCostraints
    
    @property
    def vlambda(self):
        return self._vlambda
    
    
    def tryMove(self, temperature, useLength):
        """
        Move the path or lambda multipiers in a neighbouring state,
        with a certain acceptance probability.
        Pick a random vertex (except extremes), and move
        it in a random direction (with a maximum perturbance).
        Use a lagrangian relaxation because we need to evaluate
        min(measure(path)) given the costraint that all quadrilaters
        formed by 4 consecutive points in the path must be collision
        free; where measure(path) is, depending of the choose method,
        the length of the path or the mean
        of the supplementary angles of each pair of edges of the path.
        """

        moveVlambda = random.random() < self._changeVlambdaProbability
        if moveVlambda:
            newVlambda = self._vlambda
            newVlambda = newVlambda + (random.uniform(-1.,1.) * self._maxVlambdaPert)

            newEnergy = self._calculatePathEnergyLambda(newVlambda)

            #attention, different formula from below
            if (newEnergy > self._currentEnergy) or (math.exp(-(self._currentEnergy-newEnergy)/temperature) >= random.random()):
                self._vlambda = newVlambda
                self._currentEnergy = newEnergy
        
        else:
            moveR = random.randint(1,self._dimR - 2) #don't change extremes
            moveC = random.randint(0,self._dimC - 1)

            newVertexes = np.copy(self._vertexes)
            newVertexes[moveR][moveC] = newVertexes[moveR][moveC] + (random.uniform(-1.,1.) * self._maxVertexPert)

            newEnergy,newLength,newMeanAngle,newCostraints = self._calculatePathEnergyVertex(newVertexes, moveR, moveC, useLength)

            #attention, different formula from above
            if (newEnergy < self._currentEnergy) or (math.exp(-(newEnergy-self._currentEnergy)/temperature) >= random.random()):
                self._vertexes = newVertexes
                self._currentEnergy = newEnergy
                self._currentLength = newLength
                self._currentMeanAngle = newMeanAngle
                self._currentCostraints = newCostraints

    def _initializePathEnergy(self, vertexes, vlambda):
        length = 0.
        for i in range(1, self._dimR):
            length = length + np.linalg.norm(np.subtract(vertexes[i], vertexes[i-1]))

        
        meanAngle = 0.
        for i in range(1, self._dimR - 1): #from 1 to dimR-2
            meanAngle = meanAngle + 1. + (np.dot(np.subtract(vertexes[i-1],vertexes[i]), np.subtract(vertexes[i+1],vertexes[i])) / (np.linalg.norm(np.subtract(vertexes[i-1],vertexes[i])) * np.linalg.norm(np.subtract(vertexes[i+1],vertexes[i]))))
            #meanAngle = meanAngle / (self._dimR - 2)

        costraints = self._calculateCostraints(vertexes)

        energy = meanAngle + vlambda * costraints
        
        return (energy, length, meanAngle, costraints)
                

    def _calculatePathEnergyLambda(self, vlambda):
        """
        calculate the energy when lambda is moved.
        """
        return (self._currentEnergy - (self._vlambda * self._currentCostraints) + (vlambda * self._currentCostraints))
    
    def _calculatePathEnergyVertex(self, vertexes, moveR, moveC, useLength):
        """
        calculate the energy when a vertex is moved and returns it.
        """
        costraints = self._calculateCostraints(vertexes)
        if useLength:
            length = self._calculateLength(vertexes, moveR, moveC)
            meanAngle = self._currentMeanAngle
            energy = length + self._vlambda * costraints
        else:
            length = self._currentLength
            meanAngle = self._calculateMeanAngle(vertexes, moveR, moveC)
            energy = meanAngle + self._vlambda * costraints
            
        return (energy, length, meanAngle, costraints)

    def _calculateLength(self, vertexes, moveR, moveC):
        length = self._currentLength
        
        length = length - np.linalg.norm(np.subtract(self._vertexes[moveR], self._vertexes[moveR-1])) + np.linalg.norm(np.subtract(vertexes[moveR], vertexes[moveR-1]))
        length = length - np.linalg.norm(np.subtract(self._vertexes[moveR+1], self._vertexes[moveR])) + np.linalg.norm(np.subtract(vertexes[moveR+1], vertexes[moveR]))

        return length
    
    def _calculateMeanAngle(self, vertexes, moveR, moveC):
        meanAngle = self._currentMeanAngle
        if moveR >= 2:
            meanAngle = meanAngle - (np.dot(np.subtract(self._vertexes[moveR-2],self._vertexes[moveR-1]), np.subtract(self._vertexes[moveR],self._vertexes[moveR-1])) / (np.linalg.norm(np.subtract(self._vertexes[moveR-2],self._vertexes[moveR-1])) * np.linalg.norm(np.subtract(self._vertexes[moveR],self._vertexes[moveR-1])))) + (np.dot(np.subtract(vertexes[moveR-2],vertexes[moveR-1]), np.subtract(vertexes[moveR],vertexes[moveR-1])) / (np.linalg.norm(np.subtract(vertexes[moveR-2],vertexes[moveR-1])) * np.linalg.norm(np.subtract(vertexes[moveR],vertexes[moveR-1]))))

        meanAngle = meanAngle - (np.dot(np.subtract(self._vertexes[moveR-1],self._vertexes[moveR]), np.subtract(self._vertexes[moveR+1],self._vertexes[moveR])) / (np.linalg.norm(np.subtract(self._vertexes[moveR-1],self._vertexes[moveR])) * np.linalg.norm(np.subtract(self._vertexes[moveR+1],self._vertexes[moveR])))) + (np.dot(np.subtract(vertexes[moveR-1],vertexes[moveR]), np.subtract(vertexes[moveR+1],vertexes[moveR])) / (np.linalg.norm(np.subtract(vertexes[moveR-1],vertexes[moveR])) * np.linalg.norm(np.subtract(vertexes[moveR+1],vertexes[moveR]))))

        if moveR < self._dimR-2:
            meanAngle = meanAngle - (np.dot(np.subtract(self._vertexes[moveR],self._vertexes[moveR+1]), np.subtract(self._vertexes[moveR+2],self._vertexes[moveR+1])) / (np.linalg.norm(np.subtract(self._vertexes[moveR],self._vertexes[moveR+1])) * np.linalg.norm(np.subtract(self._vertexes[moveR+2],self._vertexes[moveR+1])))) + (np.dot(np.subtract(vertexes[moveR],vertexes[moveR+1]), np.subtract(vertexes[moveR+2],vertexes[moveR+1])) / (np.linalg.norm(np.subtract(vertexes[moveR],vertexes[moveR+1])) * np.linalg.norm(np.subtract(vertexes[moveR+2],vertexes[moveR+1]))))

        return meanAngle

    def _calculateCostraints(self, vertexes):
        """
        calculate the costraints function. Is the ratio of the points
        of the calculated spline that are inside obstacles respect the
        total number of points of the spline.
        """
        pointsInside = 0
        for p in self._splinePoints(vertexes):
            if self._scene.isInside(p):
                pointsInside = pointsInside + 1

        costraints = pointsInside / self._numPointsSpline

        return costraints

    def _splinePoints(self, vertexes):
        x = vertexes[:,0]
        y = vertexes[:,1]

        t = range(len(vertexes))
        ipl_t = np.linspace(0.0, len(vertexes) - 1, self._numPointsSpline)
        x_tup = si.splrep(t, x, k=4)
        y_tup = si.splrep(t, y, k=4)

        x_list = list(x_tup)
        xl = x.tolist()
        x_list[1] = xl + [0.0, 0.0, 0.0, 0.0]

        y_list = list(y_tup)
        yl = y.tolist()
        y_list[1] = yl + [0.0, 0.0, 0.0, 0.0]

        x_i = si.splev(ipl_t, x_list)
        y_i = si.splev(ipl_t, y_list)

        return np.vstack((x_i,y_i)).T

        
    def plot(self, plotter, plotStartEnd=True, plotInnerVertexes=False, plotEdges=True, plotSpline=True):
        if plotEdges:
            plotter.plot(self._vertexes[:,0], self._vertexes[:,1], 'r--')
        if plotStartEnd:
            plotter.plot(self._vertexes[0,0], self._vertexes[0,1], 'ro')
            plotter.plot(self._vertexes[-1,0], self._vertexes[-1,1], 'ro')
        if plotInnerVertexes:
            plotter.plot(self._vertexes[1:-1,0], self._vertexes[1:-1,1], 'ro')
        if plotSpline:
            spline = self._splinePoints(self._vertexes)
            plotter.plot(spline[:,0], spline[:,1], 'r', lw=2)

