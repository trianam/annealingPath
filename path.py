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
    _numSigmaGauss = 9
    
    def __init__(self, initialVertexes, scene):
        self._vertexes = initialVertexes
        self._scene = scene
        self._dimR = self._vertexes.shape[0]
        self._dimC = self._vertexes.shape[1]
        self._numPointsSpline = self._numPointsSplineMultiplier * self._dimR
        self._spline = self._splinePoints(self._vertexes)
        self._vlambda = self._initialVlambda 
        self._currentEnergy, self._currentLength, self._currentMeanAngle, self._currentCostraints = self._initializePathEnergy(self._vertexes, self._spline, self._vlambda)

    @property
    def vertexes(self):
        return self._vertexes

    @property
    def spline(self):
        return self._spline

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
    
    
    def tryMove(self, temperature, useLength, neighbourMode):
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
            newVertexes = np.copy(self._vertexes)
            movedV = random.randint(1,self._dimR - 2) #don't change extremes

            if(neighbourMode == 0):
                moveC = random.randint(0,self._dimC - 1)
                newVertexes[movedV][moveC] = newVertexes[movedV][moveC] + (random.uniform(-1.,1.) * self._maxVertexPert)
            else:
                a = self._vertexes[movedV-1] - self._vertexes[movedV+1]
                b = np.array([1,0])
                
                alfa = math.acos(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))) - (math.pi/2)
                randAng = self._truncGauss(math.pi/2, math.pi/(2*self._numSigmaGauss), 0, math.pi)
                if random.randint(0,self._dimC - 1) == 1:
                    randAng = randAng + math.pi

                randAng = randAng + alfa

                randDist = random.uniform(-1.,1.) * self._maxVertexPert

                newVertexes[movedV] = self._vertexes[movedV] + np.array([randDist * math.cos(randAng), randDist * math.sin(randAng)])
#                newVertexes[movedV][0] = newVertex[0]
#                newVertexes[movedV][1] = newVertex[1]
                            
                
            newSpline,newEnergy,newLength,newMeanAngle,newCostraints = self._calculatePathEnergyVertex(newVertexes, movedV, useLength)

            #attention, different formula from above
            if (newEnergy < self._currentEnergy) or (math.exp(-(newEnergy-self._currentEnergy)/temperature) >= random.random()):
                self._vertexes = newVertexes
                self._spline = newSpline
                self._currentEnergy = newEnergy
                self._currentLength = newLength
                self._currentMeanAngle = newMeanAngle
                self._currentCostraints = newCostraints

    def _truncGauss(self, mu, sigma, bottom, top):
        v = random.gauss(mu,sigma)
        while not (bottom <= v <= top):
            v = random.gauss(mu,sigma)
        return v
        
    def _initializePathEnergy(self, vertexes, spline, vlambda):
        length = 0.
        for i in range(1, self._dimR):
            length = length + np.linalg.norm(np.subtract(vertexes[i], vertexes[i-1]))

        
        meanAngle = 0.
        for i in range(1, self._dimR - 1): #from 1 to dimR-2
            meanAngle = meanAngle + 1. + (np.dot(np.subtract(vertexes[i-1],vertexes[i]), np.subtract(vertexes[i+1],vertexes[i])) / (np.linalg.norm(np.subtract(vertexes[i-1],vertexes[i])) * np.linalg.norm(np.subtract(vertexes[i+1],vertexes[i]))))
            #meanAngle = meanAngle / (self._dimR - 2)

        costraints = self._calculateCostraints(spline)

        energy = meanAngle + vlambda * costraints
        
        return (energy, length, meanAngle, costraints)
                

    def _calculatePathEnergyLambda(self, vlambda):
        """
        calculate the energy when lambda is moved.
        """
        return (self._currentEnergy - (self._vlambda * self._currentCostraints) + (vlambda * self._currentCostraints))
    
    def _calculatePathEnergyVertex(self, vertexes, movedV, useLength):
        """
        calculate the energy when a vertex is moved and returns it.
        """
        spline = self._splinePoints(vertexes)
        costraints = self._calculateCostraints(spline)
        if useLength:
            length = self._calculateLength(vertexes, movedV)
            meanAngle = self._currentMeanAngle
            energy = length + self._vlambda * costraints
        else:
            length = self._currentLength
            meanAngle = self._calculateMeanAngle(vertexes, movedV)
            energy = meanAngle + self._vlambda * costraints
            
        return (spline, energy, length, meanAngle, costraints)

    def _calculateLength(self, vertexes, movedV):
        length = self._currentLength
        
        length = length - np.linalg.norm(np.subtract(self._vertexes[movedV], self._vertexes[movedV-1])) + np.linalg.norm(np.subtract(vertexes[movedV], vertexes[movedV-1]))
        length = length - np.linalg.norm(np.subtract(self._vertexes[movedV+1], self._vertexes[movedV])) + np.linalg.norm(np.subtract(vertexes[movedV+1], vertexes[movedV]))

        return length
    
    def _calculateMeanAngle(self, vertexes, movedV):
        meanAngle = self._currentMeanAngle
        if movedV >= 2:
            meanAngle = meanAngle - (np.dot(np.subtract(self._vertexes[movedV-2],self._vertexes[movedV-1]), np.subtract(self._vertexes[movedV],self._vertexes[movedV-1])) / (np.linalg.norm(np.subtract(self._vertexes[movedV-2],self._vertexes[movedV-1])) * np.linalg.norm(np.subtract(self._vertexes[movedV],self._vertexes[movedV-1])))) + (np.dot(np.subtract(vertexes[movedV-2],vertexes[movedV-1]), np.subtract(vertexes[movedV],vertexes[movedV-1])) / (np.linalg.norm(np.subtract(vertexes[movedV-2],vertexes[movedV-1])) * np.linalg.norm(np.subtract(vertexes[movedV],vertexes[movedV-1]))))

        meanAngle = meanAngle - (np.dot(np.subtract(self._vertexes[movedV-1],self._vertexes[movedV]), np.subtract(self._vertexes[movedV+1],self._vertexes[movedV])) / (np.linalg.norm(np.subtract(self._vertexes[movedV-1],self._vertexes[movedV])) * np.linalg.norm(np.subtract(self._vertexes[movedV+1],self._vertexes[movedV])))) + (np.dot(np.subtract(vertexes[movedV-1],vertexes[movedV]), np.subtract(vertexes[movedV+1],vertexes[movedV])) / (np.linalg.norm(np.subtract(vertexes[movedV-1],vertexes[movedV])) * np.linalg.norm(np.subtract(vertexes[movedV+1],vertexes[movedV]))))

        if movedV < self._dimR-2:
            meanAngle = meanAngle - (np.dot(np.subtract(self._vertexes[movedV],self._vertexes[movedV+1]), np.subtract(self._vertexes[movedV+2],self._vertexes[movedV+1])) / (np.linalg.norm(np.subtract(self._vertexes[movedV],self._vertexes[movedV+1])) * np.linalg.norm(np.subtract(self._vertexes[movedV+2],self._vertexes[movedV+1])))) + (np.dot(np.subtract(vertexes[movedV],vertexes[movedV+1]), np.subtract(vertexes[movedV+2],vertexes[movedV+1])) / (np.linalg.norm(np.subtract(vertexes[movedV],vertexes[movedV+1])) * np.linalg.norm(np.subtract(vertexes[movedV+2],vertexes[movedV+1]))))

        return meanAngle

    def _calculateCostraints(self, spline):
        """
        calculate the costraints function. Is the ratio of the points
        of the calculated spline that are inside obstacles respect the
        total number of points of the spline.
        """
        pointsInside = 0
        for p in spline:
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
            plotter.plot(self._spline[:,0], self._spline[:,1], 'r', lw=2)

