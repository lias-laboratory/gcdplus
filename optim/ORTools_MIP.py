# 
# FIND OPTIMAL OFFSETS OF TASKS
# 
# Scheduling of non-preemptive periodic tasks with defined execution time.
# Using: MIP (Python API for ORTools - Google)
# 
# Developped by Matheus Ladeira
# LIAS (ISAE-ENSMA)

# -----------------------------------------------------------
# Import tools

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from basicFunctions.toImport import *
from ortools.linear_solver import pywraplp


# Masks

def optimizeORToolsMIP_Sum(taskSet, timeLimit_Sec = None, verbose = False):
    return optimizeORToolsMIP(taskSet, maxOverlap = False, timeLimit_Sec = timeLimit_Sec, verbose = verbose)

def optimizeORToolsMIP_Max(taskSet, timeLimit_Sec = None, verbose = False):
    return optimizeORToolsMIP(taskSet, maxOverlap = True, timeLimit_Sec = timeLimit_Sec, verbose = verbose)


# Function

def optimizeORToolsMIP(taskSet, maxOverlap = False, timeLimit_Sec = None, verbose = False):

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
    # OPTIMISATION
    # -----------------------------------------------------------

    # -----
    # MIP solver

    # Create MIP solver with the SCIP backend
    solver = pywraplp.Solver.CreateSolver('SCIP')

    # # Linear solver with the GLOP backend?
    # solver = pywraplp.Solver.CreateSolver('GLOP')

    infinity = solver.infinity()

    offsets = [solver.IntVar(0, offsetLimits[i]-1, f'O_{i}') for i in range(n)]
    k = [[solver.IntVar(-max(periods[i], periods[j])//gcds[i][j], max(periods[i], periods[j])//gcds[i][j], f'k_{i}_{j}') for j in range(n)] for i in range(n)]
    m = [[solver.IntVar(0, (gcds[i][j] - c[i]) if (gcds[i][j] - c[i] > 0) else 0, f'm_{i}_{j}') for j in range(n)] for i in range(n)]

    for i in range(n):
        for j in range(n):
            solver.Add( 0 <= offsets[j] - offsets[i] + k[i][j] * gcds[i][j] )
            solver.Add( offsets[j] - offsets[i] + k[i][j] * gcds[i][j] <= gcds[i][j]-1 )
            solver.Add( c[i] - (offsets[j] - offsets[i] + k[i][j] * gcds[i][j]) + m[i][j] >= 0 )

    weight = [[int(hyperperiod / periods[j]) if i != j else 0 for j in range(n)] for i in range(n)]

    if maxOverlap:
        maxObjective = max([max(weight[i]) for i in range(n)]) * max(c)
        objective = solver.IntVar(0, maxObjective, 'objective')
        for i in range(n):
            for j in range(n):
                solver.Add( objective >= weight[i][j] * (c[i] - (offsets[j] - offsets[i] + k[i][j] * gcds[i][j]) + m[i][j]) )
        solver.Minimize( objective )
    else:
        solver.Minimize( solver.Sum([ solver.Sum([ (c[i] - (offsets[j] - offsets[i] + k[i][j] * gcds[i][j]) + m[i][j]) * weight[i][j] for j in range(n)]) for i in range(n) ]) )

    if timeLimit_Sec != None: solver.set_time_limit( int(timeLimit_Sec * 1000) )

    status = solver.Solve()

    optimalOffsets = tuple( [int(offsets[i].solution_value()) for i in range(n)] )

    if verbose:
        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            print('Solution:')
            print('Objective value =', solver.Objective().Value())
            print('Offsets:')
            for i in range(n):
                print(f'O_{i} = {optimalOffsets[i]}')
                for j in range(n):
                    if i != j: print( f'overlap{i}_{j} = {c[i] - (offsets[j].solution_value() - offsets[i].solution_value() + k[i][j].solution_value() * gcds[i][j]) + m[i][j].solution_value()}' )
            print('Problem solved in %f milliseconds' % solver.wall_time())
        else:
            print(status)
            print('The problem does not have a feasible solution.')
            
    return optimalOffsets