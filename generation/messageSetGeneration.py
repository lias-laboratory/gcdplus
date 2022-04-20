# 
# GENERATE MESSAGE SET
# 
# Developped by Yuri Hérouard
# LIAS (ISAE-ENSMA)


# -----------------------------------------------------------
# Import

import numpy as np
import random
import csv
from drs import drs


# -----------------------------------------------------------
# Read the matrix csv file

def getMatrixFromFile(periodFactorFile):
    with open(periodFactorFile+'.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        matrix = list(reader)
        matrix = list(map(list, (map(int, x) for x in matrix)))
    return matrix


# -----------------------------------------------------------
# Algorithm 1

def generatePeriodFromFactorMatrix (matrix) :
    period = 1
    for i in range(len(matrix)):
        p = random.randrange(0, len(matrix[i]), 1)
        period = period * matrix[i][p]
    return period


# -----------------------------------------------------------
# Algorithm 2, generates a task/message set

def generateTaskSet(factorMatrix, n, u1, u2, U, granularity = 1, minExecTime = 1) :
    current_load = 0
    task_set = []
    i = 0
    while current_load < U and i < n :
        Ti = 0
        Ci = 0
        Ui = 0
        umin = 0
        while (Ti < minExecTime) or (umin > u2):
            Ti = generatePeriodFromFactorMatrix(factorMatrix)
            umin = max(u1, minExecTime/Ti)
            Ui = np.random.uniform(umin, u2)
            Ci = (round(Ui*Ti)//granularity)*granularity
        if (current_load + (Ci/Ti)) <= 1:
            current_load = current_load + (Ci/Ti)
            task_set.append({'period': Ti, 'execTime': Ci})
        i += 1
    return tuple(task_set)


# -----------------------------------------------------------
# Adapted Algorithm 2 -- added DRS

def generateTaskSetDRS(periodFactorFile, n, U, uMin = 0, uMax = 1, granularity = 1, minExecTime = 1) :    
    factorMatrix = getMatrixFromFile(periodFactorFile)
    task_set = []
    i = 0
    uVec = drs(n, U, [uMax]*n, [uMin]*n)
    fail = False
    while i < n :
        Ui = uVec[i]
        Ti = generatePeriodFromFactorMatrix(factorMatrix)
        Ci = round(Ui*Ti/granularity) * granularity
        if Ci < minExecTime: fail = True
        task_set.append({'period': Ti, 'execTime': Ci})
        i += 1
    if fail: return generateTaskSetDRS(periodFactorFile, n, U, uMin, uMax, granularity, minExecTime)
    else: return tuple(task_set)


# -----------------------------------------------------------
# Generate task from matrix in csv file

def generateMessageSet(periodFactorFile, n, u1=0, u2=0, U=1, bitsPerByte=10, headerSize_bytes=9):
    if u2==0: u2 = U/n
    factorMatrix = getMatrixFromFile(periodFactorFile)
    messageSet = generateTaskSet(factorMatrix, n, u1, u2, U, granularity = bitsPerByte, minExecTime = headerSize_bytes * bitsPerByte)
    return messageSet


