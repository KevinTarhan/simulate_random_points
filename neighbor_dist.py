# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 12:17:03 2015

@author: george
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
import math
import os


def distances(filename1, filename2, output):
    x = np.loadtxt(filename1, usecols=(0,))
    y = np.loadtxt(filename1, usecols=(1,))
    # print('File1 Loaded')

    if filename2 != 'random':
        x2 = np.loadtxt(filename2, usecols=(0,))
        y2 = np.loadtxt(filename2, usecols=(1,))
        print('File2 Loaded')

    else:
        x2, y2 = generateRandom(x, y)
        print('Random points generated')

    data = np.vstack((x, y))
    comparisonSet = np.vstack((x2, y2))
    searchRadius = 2000


    def getNeighbours(x, y, comparisonSet, searchRadius):
        keptX = []
        keptY = []
        for i in range(comparisonSet[0].size):
            if abs(x - comparisonSet[0][i]) < searchRadius and abs(y - comparisonSet[1][i]) < searchRadius:
                keptX.append(comparisonSet[0][i])
                keptY.append(comparisonSet[1][i])
        answer = np.vstack((keptX, keptY))
        return answer

    def getDistances(x, y, searchSet, searchRadius):
        answer = []
        for i in range(searchSet[0].size):
            dist = ((x - searchSet[0][i]) * (x - searchSet[0][i])) + ((y - searchSet[1][i]) * (y - searchSet[1][i]))
            dist = math.sqrt(dist)
            if dist < searchRadius:
                answer.append(dist)
        # print(answer)
        return answer

    def allDists(dataSet, comparisonSet, searchRadius):
        dataDist = []
        for i in range(dataSet[0].size):
            distance1 = (getDistances(dataSet[0][i], dataSet[1][i],
                                      getNeighbours(dataSet[0][i], dataSet[1][i], comparisonSet, searchRadius),
                                      searchRadius))
            for s in range(len(distance1)):
                dataDist.append(distance1[s])
            print(int((i / dataSet[0].size) * 100), "%")
        return dataDist



    distanceSet = allDists(data, comparisonSet, searchRadius)
    print(data)
    np.savetxt(output, np.transpose(distanceSet), delimiter=',')
    print("Result File Saved")
    return


def generateRandom(x, y):
    N = 100000
    minX = min(x)
    maxX = max(x)
    minY = min(y)
    maxY = max(y)

    x = np.random.random_integers(minX, maxX, N)
    y = np.random.random_integers(minY, maxY, N)

    print(x)
    print(y)
    return x, y


