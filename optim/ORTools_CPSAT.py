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
from ortools.sat.python import cp_model


# Masks

def optimizeORToolsCPSAT_Sum(taskSet, timeLimit_Sec = None, verbose = False):
    return optimizeORToolsCPSAT(taskSet, maxOverlap = False, timeLimit_Sec = timeLimit_Sec, verbose = verbose)

def optimizeORToolsCPSAT_Max(taskSet, timeLimit_Sec = None, verbose = False):
    return optimizeORToolsCPSAT(taskSet, maxOverlap = True, timeLimit_Sec = timeLimit_Sec, verbose = verbose)


# Function

def optimizeORToolsCPSAT(taskSet, maxOverlap = False, timeLimit_Sec = None, verbose = False):

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
    # CP-SAT solver

    # Create CP-SAT solver
    model = cp_model.CpModel()

    offsets = [model.NewIntVar(0, offsetLimits[i]-1, f'O_{i}') for i in range(n)]
    k = [[ model.NewIntVar(-max(periods[i], periods[j])//gcds[i][j], max(periods[i], periods[j])//gcds[i][j], 'k_{i}_{j}') for j in range(n) ]  for i in range(n) ]
    m = [[ model.NewIntVar(0, (gcds[i][j] - c[i]) if (gcds[i][j] - c[i] > 0) else 0, 'm_{i}_{j}') for j in range(n) ]  for i in range(n) ]

    weight = [[int(hyperperiod / periods[j]) if i != j else 0 for j in range(n)] for i in range(n)]

    for i in range(n):
        for j in range(n):
            if i != j:
                # (offsets[j] - offsets[i]) % gcds[i][j]
                model.Add( 0 <= offsets[j] - offsets[i] + k[i][j] * gcds[i][j] )
                model.Add( offsets[j] - offsets[i] + k[i][j] * gcds[i][j] <= gcds[i][j]-1 )

                model.Add( c[i] - (offsets[j] - offsets[i] + k[i][j] * gcds[i][j]) + m[i][j] >= 0 )

    # if maxOverlap:
    #     maxObjective = max([max(weight[i]) for i in range(n)]) * max(c)
    #     objective = model.NewIntVar(0, maxObjective, 'objective')
    #     for i in range(n):
    #         for j in range(n):
    #             model.Add( objective >= weight[i][j] * (c[i] - (offsets[j] - offsets[i] + k[i][j] * gcds[i][j]) + m[i][j]) )
    #     model.Minimize( objective )
    # else:
    #     model.Add( cp_model.LinearExpr.Sum([ cp_model.LinearExpr.Sum([ weight[i][j] * (c[i] - (offsets[j] - offsets[i] + k[i][j] * gcds[i][j]) + m[i][j]) for j in range(n) ]) for i in range(n) ]) >= 0 )
    #     model.Minimize( cp_model.LinearExpr.Sum([ cp_model.LinearExpr.Sum([ weight[i][j] * (c[i] - (offsets[j] - offsets[i] + k[i][j] * gcds[i][j]) + m[i][j]) for j in range(n) ]) for i in range(n) ]) )

    for i in range(n):
        for j in range(n):
            if i != j: model.Add( 0 == c[i] - (offsets[j] - offsets[i] + k[i][j] * gcds[i][j]) + m[i][j] )

    solver = cp_model.CpSolver()
    if timeLimit_Sec != None: solver.parameters.max_time_in_seconds = timeLimit_Sec
    
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL: print('Status = OPTIMAL')
    if status == cp_model.FEASIBLE: print('Status = FEASIBLE')
    if status == cp_model.UNKNOWN: print('Status = UNKNOWN')
    if status == cp_model.MODEL_INVALID: print('Status = MODEL_INVALID')
    if status == cp_model.INFEASIBLE: print('Status = INFEASIBLE')

    success = (status == cp_model.OPTIMAL or status == cp_model.FEASIBLE)
    if verbose:
        if success:
            if status == cp_model.OPTIMAL: print('Status = OPTIMAL')
            if status == cp_model.FEASIBLE: print('Status = FEASIBLE')
            print('Minimum cost: %i' % solver.ObjectiveValue())
            print()
            for i in range(n):
                print(f'O_{i} = {solver.Value(offsets[i])}')
                for j in range(n):
                    if i != j: print( f'overlap{i}_{j} = {solver.Value(c[i] - (offsets[j] - offsets[i] + k[i][j] * gcds[i][j]) + m[i][j])}' )
        else:
            print('No feasible solution found.')
            if status == cp_model.UNKNOWN: print('Status = UNKNOWN')
            if status == cp_model.MODEL_INVALID: print('Status = MODEL_INVALID')
            if status == cp_model.INFEASIBLE: print('Status = INFEASIBLE')
        print('Problem solved in %f seconds' % solver.WallTime())

    if success: optimalOffsets = tuple( [solver.Value(offsets[i]) for i in range(n)] )
    else: optimalOffsets = tuple([0]*n)

    return optimalOffsets