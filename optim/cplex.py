#/usr/bin/env python3

# 
# FIND OPTIMAL OFFSETS OF TASKS - CPLEX
# 
# Scheduling of non-preemptive periodic tasks with defined execution time.
# Using: CPLEX (Python API)
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
from docplex.cp.model import CpoModel


# Masks

def optimizeCPLEX_Sum(taskSet, timeLimit_Sec = None, verbose = False):
    return optimizeCPLEX(taskSet, maxOverlap = False, timeLimit_Sec = timeLimit_Sec, verbose = verbose)

def optimizeCPLEX_Max(taskSet, timeLimit_Sec = None, verbose = False):
    return optimizeCPLEX(taskSet, maxOverlap = True, timeLimit_Sec = timeLimit_Sec, verbose = verbose)


# Function

def optimizeCPLEX(taskSet, maxOverlap = False, timeLimit_Sec = None, verbose = False):

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
    # OPTIMIZATION
    # -----------------------------------------------------------

    # Create an instance of a linear problem to solve
    problem = CpoModel()

    # Decision variables: offsets
    offsets = [problem.integer_var(0, offsetLimits[i]-1, f'O_{i}') for i in range(n)]

    # Intermediate decision variables
    k = [[ problem.integer_var(min=-max(periods[i], periods[j])//gcds[i][j], max=max(periods[i], periods[j])//gcds[i][j], name=f'k_{i}') for j in range(n) ] for i in range(n) ]           # for linearizing a mod expression
    m = [[ problem.float_var(min=0, max = (gcds[i][j] - c[i]) if (gcds[i][j] - c[i] > 0) else 0, name=f'm_{i}') for j in range(n) ] for i in range(n) ]    # for linearizing the discontinuity when considering value 0 for every non-overlap

    # Linearization
    for i in range(n):
        for j in range(n):
            problem.add_constraint( 0 <= offsets[j] - offsets[i] + k[i][j] * gcds[i][j] )                   # (offsets[j] - offsets[i]) mod gcds[i][j]
            problem.add_constraint( offsets[j] - offsets[i] + k[i][j] * gcds[i][j] <= gcds[i][j]-1 )        # (offsets[j] - offsets[i]) mod gcds[i][j]
            problem.add_constraint( c[i] - (offsets[j] - offsets[i] + k[i][j] * gcds[i][j]) + m[i][j] >= 0 )  # overlap = 0 if c[i] - (offsets[j] - offsets[i]) mod gcds[i][j] > 0        |_/|

    # Construct cost matrix
    weight = [[int(hyperperiod / periods[j]) if i != j else 0 for j in range(n)] for i in range(n)]

    costMatrix = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j : costMatrix[i][j] = (c[i] - (offsets[j] - offsets[i] + k[i][j] * gcds[i][j]) + m[i][j]) * weight[i][j]

    # Optimisation
    if maxOverlap:
        problem.minimize( problem.max( [ problem.max( [costMatrix[i][j] for j in range(n)] ) for i in range(n) ] ) )
    else:
        problem.minimize( problem.sum( [ problem.sum( [costMatrix[i][j] for j in range(n)] ) for i in range(n) ] ) )

    if timeLimit_Sec != None: solution = problem.solve(TimeLimit=timeLimit_Sec, ObjectiveLimit=0, execfile='/opt/ibm/ILOG/CPLEX_Studio201/cpoptimizer/bin/x86-64_linux/cpoptimizer', trace_log=False)   # agent='local'
    else: problem.solve(ObjectiveLimit=0, execfile='/opt/ibm/ILOG/CPLEX_Studio201/cpoptimizer/bin/x86-64_linux/cpoptimizer', trace_log=False)

    if verbose:
        if solution:
            print(f"Solution status: {solution.get_solve_status()}")
            print(f"Objective values: {solution.get_objective_values()}")
            for i in range(n): print(f'O_{i} = {solution[offsets[i]]}')
        else:
            print("No solution found")
        
    # if not solution:
    #     print(periods)
    #     print(c)
    #     print(hyperperiod)
    #     print(reduce(gcd, periods))
    #     input(solution.get_solve_status())

    optimalOffsets = tuple( [solution[offsets[i]] for i in range(n)] ) if solution else tuple([0] * n)
    return optimalOffsets