
# 
# FIND OPTIMAL OFFSETS OF TASKS
# 
# Scheduling of non-preemptive periodic tasks with defined execution time.
# Using: OMT (Python API for Z3 tool)
# 
# Developped by Matheus Ladeira
# LIAS (ISAE-ENSMA)

# -----------------------------------------------------------
# Import tools

import os, sys
from threading import TIMEOUT_MAX
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from z3 import *
from basicFunctions.toImport import *
from time import time as now


# Masks

def optimizeZ3_Sum(taskSet, timeLimit_Sec = None, verbose = False):
    return optimizeZ3(taskSet, maxOverlap = False, timeLimit_Sec = timeLimit_Sec, verbose = verbose)

def optimizeZ3_Max(taskSet, timeLimit_Sec = None, verbose = False):
    return optimizeZ3(taskSet, maxOverlap = True, timeLimit_Sec = timeLimit_Sec, verbose = verbose)


# Function

def optimizeZ3(taskSet, maxOverlap = False, timeLimit_Sec = None, verbose = False):

    n = len(taskSet)

    periods = tuple( [ int(round(task['period'] )) for task in taskSet ] )
    c = tuple( [ task['execTime'] for task in taskSet ] )

    gcds = tuple( [ tuple( [gcd(periods[i], periods[j]) for j in range(n)] ) for i in range(n)] )

    offsetLimits = [0] * n
    currentLCM = 1
    for i in range(n):
        offsetLimits[i] = gcd(periods[i], int(currentLCM))
        currentLCM = (currentLCM / offsetLimits[i]) * periods[i]

    hyperperiod = reduce(lcm, periods)

    if verbose:
        print(f'\nOPTIMISATION OF {n} TASK OFFSETS\n')

        print('Tasks:')
        print()
        print('i'.rjust(3) + '| TASK_ID'.ljust(24) + '| c (bits)'.ljust(11) + '| T (ticks)'.ljust(12))
        print(''.rjust(60, '-'))
        for i in range(n):
            print(f'{i:>3}| {c[i]:<8} | {periods[i]:>9}')
        print()

    # -----------------------------------------------------------
    # Optimisation

    offsets = IntVector('R', n)
    k = [[ Int("k_%s_%s" % (i, j)) for j in range(n) ] for i in range(n) ]
    m = [[ Int("m_%s_%s" % (i, j)) for j in range(n) ] for i in range(n) ]

    opt = Optimize()

    # Offsets are always between 0 and GCD(Ti, LCM(preceeding tasks))
    opt.add( [And( offsets[i] >= 0 , offsets[i] < offsetLimits[i] ) for i in range(n)] )

    opt.add( [And( k[i][j] >= -max(periods[i], periods[j])//gcds[i][j] , k[i][j] <= max(periods[i], periods[j])//gcds[i][j] ) for j in range(n) for i in range(n)] )
    opt.add( [And( m[i][j] >= 0 , m[i][j] <= ((gcds[i][j] - c[i]) if (gcds[i][j] - c[i] > 0) else 0) ) for j in range(n) for i in range(n)] )


    for i in range(n):
        for j in range(n):
            opt.add( And(0 <= offsets[j] - offsets[i] + k[i][j] * gcds[i][j], offsets[j] - offsets[i] + k[i][j] * gcds[i][j] <= gcds[i][j]-1) )
            opt.add( And(c[i] - (offsets[j] - offsets[i] + k[i][j] * gcds[i][j]) + m[i][j] >= 0, m[i][j] >= 0) )

    weight = [[int(hyperperiod / periods[j]) if i != j else 0 for j in range(n)] for i in range(n)]

    objective = Int('objective')
    opt.add( objective >= 0 )

    if maxOverlap:
        for i in range(n):
            for j in range(n):
                opt.add( objective >= weight[i][j] * (c[i] - (offsets[j] - offsets[i] + k[i][j] * gcds[i][j]) + m[i][j]) )
    else:
        opt.add( objective == Sum([ Sum([ (c[i] - (offsets[j] - offsets[i] + k[i][j] * gcds[i][j]) + m[i][j]) * weight[i][j] for j in range(n) ]) for i in range(n) ]) )
    
    h = opt.minimize( objective )

    if timeLimit_Sec != None: opt.set( timeout = int(timeLimit_Sec * 1000) )

    if verbose: print(opt.sexpr)
    start = now()
    output = opt.check()
    end = now()
    if verbose:
        print(output)
        print(opt.reason_unknown())
        print(opt.model())
        print( end - start )

    if opt.model(): optimalOffsets = tuple( [ opt.model()[offsets[i]].as_long() for i in range(n)] )
    else: optimalOffsets = tuple( [0] * n )
    if verbose:
        for i in range(n):
            print(opt.model()[offsets[i]])
    
    return optimalOffsets