#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
import voronizator
import polygon
import scene
import oven

scene = scene.Scene()
maxEmptyLen = 0.1
#poly1 = polygon.Polygon(vertexes=np.array([[0.1,0.1],[0.2,0.3],[0.25,0.45],[0.15,0.4]]), maxEmptyLen=maxEmptyLen)
poly1 = polygon.Polygon(vertexes=np.array([[0.,0.],[0.2,0.5],[0.5,0.1],[0.7,0.4],[1.,0.]]), maxEmptyLen=maxEmptyLen)
poly2 = polygon.Polygon(vertexes=np.array([[0.,1.],[0.05,0.4],[0.3,0.7],[0.5,0.2],[0.7,0.5],[0.9,0.4],[1.,1.]]), maxEmptyLen=maxEmptyLen)

fig = plt.figure()
ax = fig.gca()

#Vs = np.array([-0.5,0.5])
#Ve = np.array([1.5,0.5])
Vs = np.array([-0.1,0.5])
Ve = np.array([1.1,0.5])

scene.addPolygon(poly1)
scene.addPolygon(poly2)
#scene.addPolygon(poly3)

#scene.addBoundingBox([-1.,-1.], [2.,2.], maxEmptyLen=.2)
scene.addBoundingBox([-0.25,-0.25], [1.25,1.25], maxEmptyLen=.2)

voronoi = voronizator.Voronizator(scene)
oven = oven.Oven(trials=100, warmingRatio=0.9)

voronoi.makeVoroGraph()
path = voronoi.createShortestPath(Vs, Ve, attachMode='near', minEdgeLen=0.05, maxEdgeLen=0.08, optimizeVal='maxCurvatureLength')
#voronoi.calculateShortestPath(Vs, Ve, 'all')
#oven.anneal(path, neighbourMode=1)
oven.annealAnimation(path, fig, ax, neighbourMode=0)

voronoi.plotSites(ax)
scene.plot(ax)
#voronoi.plotGraph(ax, edges=False, labels=True)
#voronoi.plotGraph(ax, pathExtremes=True)
#voronoi.plotGraph(ax)
#path.plot(ax,plotInnerVertexes=True,plotSpline=True)

#ax.set_xlim(-1., 2.)
#ax.set_ylim(-1., 2.)
ax.set_xlim(-0.25, 1.25)
ax.set_ylim(-0.25, 1.25)

ax.set_xlabel('x')
ax.set_ylabel('y')

plt.show()
