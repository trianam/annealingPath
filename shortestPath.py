#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
import voronizator
import polygon

voronoi = voronizator.Voronizator()

maxEmptyLen = 0.1
poly1 = polygon.Polygon(vertexes=np.array([[0.1,0.1],[0.2,0.3],[0.25,0.45],[0.15,0.4]]), maxEmptyLen=maxEmptyLen)

fig = plt.figure()
ax = fig.gca()

Vs = np.array([-0.5,-0.5])
Ve = np.array([1.,1.])

voronoi.addPolygon(poly1)
#voronoi.addPolygon(poly2)
#voronoi.addPolygon(poly3)

voronoi.addBoundingBox([-1.,-1.], [2.,2.], maxEmptyLen=.2)
voronoi.setPolygonsSites()
voronoi.makeVoroGraph()
voronoi.calculateShortestPath(Vs, Ve, attachMode='near', minEdgeLen=0.05, maxEdgeLen=0.1)
#voronoi.calculateShortestPath(Vs, Ve, 'all')

voronoi.plotSites(ax)
voronoi.plotPolygons(ax)
#voronoi.plotGraph(ax, edges=False, labels=True)
#voronoi.plotGraph(ax, pathExtremes=True)
#voronoi.plotGraph(ax)
voronoi.plotShortestPath(ax,plotInnerVertexes=True,plotSpline=False)

ax.set_xlim(-1., 2.)
ax.set_ylim(-1., 2.)

# ax.set_xlim(0., 1.)
# ax.set_ylim(0., 1.)

ax.set_xlabel('x')
ax.set_ylabel('y')

plt.show()
