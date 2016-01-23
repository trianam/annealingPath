import smoothener

class Path:
    def __init__(self, initialVertexes):
        self._smoothener = smoothener.Smoothener()
        self._vertexes = initialVertexes

    def plot(self, plotter, plotStartEnd=True, plotInnerVertexes=False, plotEdges=True, plotSpline=True):
        if self._vertexes.size > 0:
            self._smoothener.plot(self._vertexes, plotter, plotStartEnd, plotInnerVertexes, plotEdges, plotSpline)
