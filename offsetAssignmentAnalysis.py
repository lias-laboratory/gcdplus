# 
# OFFSET ASSIGNMENT ANALYSIS
# 
# Compare Calculation Time and Delay Performance of different offset assignment strategies
#
# Developped by Yuri Hérouard
# LIAS (ISAE-ENSMA)


# -----------------------------------------------------------
# Input variables

factorMatrixFile = 'default_rotorcraft_xmlMatrix'      # WITHOUT EXTENTION - Name of the file containing the matrix of period factors, for task generation
outputFolderRoot = 'res'              # WITHOUT EXTENTION - Root for the name of the files containing the results

filterSets = True                   # True | False -- Enable filtering task sets with large enough GCDs

heur_new = True                     # True | False -- Enable analysis of New Heuristics
heur_goossens = False                # True | False -- Enable analysis of Goossens Scheduling
heur_goossensModified = False        # True | False -- Enable analysis of Modified Goossens (with lengths) Scheduling
heur_goossensCoupled = True         # True | False -- Enable analysis of Original + Modified Goossens (with lengths) Scheduling
heur_can = True                     # True | False -- Enable analysis of CAN Scheduling
heur_paparazzi = True               # True | False -- Enable analysis of Paparazzi Scheduling
optim_cplex_max = False              # True | False -- Enable analysis of Optimization (Max Delay) Scheduling - CPLEX
optim_cplex_sum = False              # True | False -- Enable analysis of Optimization (Sum Delays) Scheduling - CPLEX
optim_ortools_cpsat_max = False      # True | False -- Enable analysis of Optimization (Max Delay) Scheduling - OR-Tools (CP-SAT)
optim_ortools_cpsat_sum = False      # True | False -- Enable analysis of Optimization (Sum Delays) Scheduling - OR-Tools (CP-SAT)
optim_ortools_mip_max = False        # True | False -- Enable analysis of Optimization (Max Delay) Scheduling - OR-Tools (MIP)
optim_ortools_mip_sum = False        # True | False -- Enable analysis of Optimization (Sum Delays) Scheduling - OR-Tools (MIP)
optim_z3_max = False                 # True | False -- Enable analysis of Optimization (Max Delay) Scheduling - Z3
optim_z3_sum = False                 # True | False -- Enable analysis of Optimization (Sum Delays) Scheduling - Z3

numberSets = 1000   # Number of sets to generate for the analysis
numberTasks = 16    # Number of tasks to generate for each set
U_target = 0.98      # Utilization factor, between 0 and 1
verbose = False     # Print progress while doing analysis

optimTimeLimit = None  # seconds


# -----------------------------------------------------------
# Import

from pathlib import Path
import csv
from time import time as now
from datetime import datetime
from math import gcd
from functools import reduce
from copy import deepcopy
from heapq import nlargest

from generation.messageSetGeneration import generateTaskSetDRS, getMatrixFromFile
from basicFunctions.simulation import getMaxDelaysFromSim
from basicFunctions.boxplot import printBoxplot4

from scheduling.ladeira import heuristicScheduling
from scheduling.goossens import goossensCoupledScheduling, goossensScheduling, goossensModifiedScheduling
from scheduling.can import CANScheduling
from scheduling.paparazzi import paparazziScheduling

from optim.cplex import optimizeCPLEX_Max, optimizeCPLEX_Sum
from optim.ORTools_CPSAT import optimizeORToolsCPSAT_Max, optimizeORToolsCPSAT_Sum
from optim.ORTools_MIP import optimizeORToolsMIP_Max, optimizeORToolsMIP_Sum
from optim.z3py import optimizeZ3_Max, optimizeZ3_Sum


# -----------------------------------------------------------
# Functions

def evalCoupledSchedHeur(heuristicFunction, list_taskSets):
    # Evaluate Coupled Scheduling Heuristics

    list_calcTime = []

    list_offsetAssignments_orig = []
    list_offsetAssignments_mod = []

    n = len(list_taskSets)
    i = 0

    for taskSet in list_taskSets:

        # Get time for calculating offsets
        start = now()
        coupledOffsets = heuristicFunction(taskSet)
        end = now()
        list_calcTime.append(end - start)
        list_offsetAssignments_orig.append( tuple(coupledOffsets[0]) )
        list_offsetAssignments_mod.append( tuple(coupledOffsets[1]) )
        i += 1

    return ( {'calcTimes': tuple(list_calcTime), 'offsets': tuple(list_offsetAssignments_orig)},
            {'calcTimes': tuple(list_calcTime), 'offsets': tuple(list_offsetAssignments_mod)} )


def evalSchedHeur(heuristicFunction, list_taskSets):
    # Evaluate Scheduling Heuristics

    list_calcTime = []

    list_offsetAssignments = []

    n = len(list_taskSets)
    i = 0

    for taskSet in list_taskSets:

        # Get time for calculating offsets
        start = now()
        offsets = heuristicFunction(taskSet)
        end = now()
        list_calcTime.append(end - start)
        list_offsetAssignments.append( tuple(offsets) )
        i += 1

    return {'calcTimes': tuple(list_calcTime), 'offsets': tuple(list_offsetAssignments)}

    
def evalOptimAlgo(optimAlgorithm, list_taskSets, timeLimit=None):
    # Evaluate Optimization Algorithm

    list_calcTime = []

    list_offsetAssignments = []

    n = len(list_taskSets)
    i = 0

    for taskSet in list_taskSets:

        start = now()
        offsets = optimAlgorithm(taskSet, timeLimit_Sec=timeLimit)
        end = now()
        list_calcTime.append(end - start)
        list_offsetAssignments.append(tuple(offsets))
        i += 1

    return {'calcTimes': tuple(list_calcTime), 'offsets': tuple(list_offsetAssignments)}



# -----------------------------------------------------------
# ------------------------ ALGORITHM ------------------------
# -----------------------------------------------------------


# To generate a factor matrix: probabilityFromXml.py

list_algorithms = []

print('EVALUATION OF FIFO OFFSET ASSIGNMENT ALGORITHMS')
print('-----------------------------------------------')
print()

print('Considering the following algorithms:')

if heur_new :                   list_algorithms.append( {'name': 'New Heuristics', 'function': heuristicScheduling} )
if heur_paparazzi :             list_algorithms.append( {'name': 'Paparazzi method', 'function': paparazziScheduling} )
if heur_goossens :              list_algorithms.append( {'name': 'Goossens\'s Heuristics', 'function': goossensScheduling} )
if heur_goossensModified :      list_algorithms.append( {'name': 'Modified Goossens\'s Heuristics', 'function': goossensModifiedScheduling} )    
if heur_goossensCoupled :       list_algorithms.append( {'name': 'Coupled Goossens\'s Heuristics', 'function': goossensCoupledScheduling} )    
if heur_can :                   list_algorithms.append( {'name': 'CAN Message Heuristics', 'function': CANScheduling} )    
if optim_cplex_max :            list_algorithms.append( {'name': 'Optim Max Norm Delay - CPLEX', 'function': optimizeCPLEX_Max, 'optimization': True} )  
if optim_cplex_sum :            list_algorithms.append( {'name': 'Optim Sum Norm Delay - CPLEX', 'function': optimizeCPLEX_Sum, 'optimization': True} )      
if optim_ortools_cpsat_max :    list_algorithms.append( {'name': 'Optim Max Norm Delay - OR-Tools CP-SAT', 'function': optimizeORToolsCPSAT_Max, 'optimization': True} )   
if optim_ortools_cpsat_sum :    list_algorithms.append( {'name': 'Optim Sum Norm Delay - OR-Tools CP-SAT', 'function': optimizeORToolsCPSAT_Sum, 'optimization': True} )  
if optim_ortools_mip_max :      list_algorithms.append( {'name': 'Optim Max Norm Delay - OR-Tools MIP', 'function': optimizeORToolsMIP_Max, 'optimization': True} )   
if optim_ortools_mip_sum :      list_algorithms.append( {'name': 'Optim Sum Norm Delay - OR-Tools MIP', 'function': optimizeORToolsMIP_Sum, 'optimization': True} )  
if optim_z3_max :               list_algorithms.append( {'name': 'Optim Max Norm Delay - Z3', 'function': optimizeZ3_Max, 'optimization': True} )          
if optim_z3_sum :               list_algorithms.append( {'name': 'Optim Sum Norm Delay - Z3', 'function': optimizeZ3_Sum, 'optimization': True} )    

list_algorithms = tuple( list_algorithms )

for algorithm in list_algorithms:
    print(' - ' + algorithm['name'])

print()

if verbose:
    print(f'Generating {numberSets} sets of {numberTasks} tasks...')
    print()
    print('Factor matrix:')
    for line in getMatrixFromFile(factorMatrixFile):
        print(line)


# ---------------------------------------------------------------------------------------
# Generate a list of Tasks Sets:

if filterSets: printFilterSets = 'filtered '
else: printFilterSets = ''
print('Generating ' + printFilterSets + 'task sets...')

list_taskSets = []
for i in range(numberSets):
    if filterSets:
        gcdPeriods = 1
        maxExecTime = 1
        while maxExecTime >= gcdPeriods:
            newTaskSet = generateTaskSetDRS(factorMatrixFile, numberTasks, U = U_target)
            gcdPeriods = reduce(gcd, [task['period'] for task in newTaskSet] )
            maxExecTime = max([task['execTime'] for task in newTaskSet])
    else:
        newTaskSet = generateTaskSetDRS(factorMatrixFile, numberTasks, U = U_target)
    list_taskSets.append( newTaskSet )
    print(f'{i+1}/{numberSets}', end='\r', flush=True)
list_taskSets = tuple(list_taskSets)
uMin = 1
uMax = 0
for taskSet in list_taskSets:
    currentU = 0
    for task in taskSet:
        currentU += task['execTime']/task['period']
    if currentU < uMin: uMin = currentU
    if currentU > uMax: uMax = currentU
print()

if filterSets: markAsfiltered = '_f'
else: markAsfiltered = ''

today = datetime.now()
outputFolder = outputFolderRoot + markAsfiltered + f'_{numberSets}x{numberTasks}t_U{U_target*100:.0f}_' + today.strftime("%y%m%d_%H%M")

taskSetsFileName = f'{outputFolder}/taskSets_{numberSets}x{numberTasks}t.csv'

Path(outputFolder).mkdir(parents=True, exist_ok=False)
with open(taskSetsFileName, "w") as file:
    writer = csv.writer(file, delimiter=';')
    file.write('(T1,c1);(T2,c2);...\n')
    for taskSet in list_taskSets:
        writer.writerow([(task["period"], task["execTime"]) for task in taskSet])


# ---------------------------------------------------------------------------------------
# Calculate offsets:

list_results = []

for algorithm in list_algorithms:

    if algorithm['name'] == 'Coupled Goossens\'s Heuristics':

        result_orig = {'name': 'Goossens\'s Heuristics (C)'}
        result_orig['taskSets'] = tuple( [ {'tasks': x} for x in list_taskSets] )

        result_mod = {'name': 'Modified Goossens\'s Heuristics (C)'}
        result_mod['taskSets'] = tuple( [ {'tasks': x} for x in list_taskSets] )
        
        coupledResult = evalCoupledSchedHeur(algorithm['function'], list_taskSets)

        for i, taskSet in enumerate(result_orig['taskSets']):
            taskSet['calcTime'] = coupledResult[0]['calcTimes'][i]
            for j, task in enumerate(taskSet['tasks']):
                task['offset'] = coupledResult[0]['offsets'][i][j]

        for i, taskSet in enumerate(result_mod['taskSets']):
            taskSet['calcTime'] = coupledResult[1]['calcTimes'][i]
            for j, task in enumerate(taskSet['tasks']):
                task['offset'] = coupledResult[1]['offsets'][i][j]
        
        list_results.append( deepcopy(result_orig) )
        list_results.append( deepcopy(result_mod) )

        print(f"Time spent in {algorithm['name']} is: ", sum(coupledResult[0]['calcTimes']))

    else:
        result = {}
        result['name'] = algorithm['name']
        result['taskSets'] = tuple( [ {'tasks': x} for x in list_taskSets] )

        if algorithm.get('optimization'): output = evalOptimAlgo(algorithm['function'], list_taskSets, timeLimit=optimTimeLimit)
        else: output = evalSchedHeur(algorithm['function'], list_taskSets)

        for i, taskSet in enumerate(result['taskSets']):
            taskSet['calcTime'] = output['calcTimes'][i]
            for j, task in enumerate(taskSet['tasks']):
                task['offset'] = output['offsets'][i][j]

        list_results.append( deepcopy(result) )
        print(f"Time spent in {algorithm['name']} is: ", sum(output['calcTimes']))


# ---------------------------------------------------------------------------------------
# Get maximum delays from simulation

print('Simulating...')

for result in list_results:
    notSchedulable = 0
    for i, taskSet in enumerate(result['taskSets']):
        schedulable = True
        maxDelays = getMaxDelaysFromSim(taskSet['tasks'], [ task['offset'] for task in taskSet['tasks'] ] )
        for j, task in enumerate(taskSet['tasks']):
            task['maxDelay'] = maxDelays[j]
            if task['maxDelay'] + task['execTime'] > task['period']: schedulable = False
        if not schedulable: notSchedulable += 1
    result['notSchedulable'] = notSchedulable


functionNameList = tuple([result['name'] for result in list_results])

allMaxDelays = tuple( [ tuple( [task['maxDelay'] for taskSet in result['taskSets'] for task in taskSet['tasks']] ) for result in list_results ] )

maxDelaysPerPeriod = tuple( [ tuple( [task['maxDelay']/task['period'] for taskSet in result['taskSets'] for task in taskSet['tasks']] ) for result in list_results ] )

maxDelaysPerExecTime = tuple( [ tuple( [
    task['maxDelay']/nlargest(2, [ t['execTime'] for t in taskSet['tasks'] ])[1 if (task['execTime'] == max([ t['execTime'] for t in taskSet['tasks'] ])) else 0]
    for taskSet in result['taskSets'] for task in taskSet['tasks']] ) for result in list_results ] )

maxRespTimeOverC = tuple( [ tuple( [
    (task['maxDelay'] + task['execTime'])/task['execTime']
    for taskSet in result['taskSets'] for task in taskSet['tasks']] ) for result in list_results ] )


# Plot in boxplot
plotFileName = f'{outputFolder}/plot_{numberSets}x{numberTasks}t'

printBoxplot4(functionNameList, allMaxDelays, maxDelaysPerPeriod, maxDelaysPerExecTime, maxRespTimeOverC, plotFileName, showOutliers=False)
printBoxplot4(functionNameList, allMaxDelays, maxDelaysPerPeriod, maxDelaysPerExecTime, maxRespTimeOverC, plotFileName+"_outliers", showOutliers=True)


# Write log in txt file
with open(outputFolder + '/log.txt', "w+") as file:
    file.write(f'{numberSets} sets of {numberTasks} tasks. U = {U_target:.2f} ({uMin:.2f} - {uMax:.2f}).\n\n')
    for result in list_results:
        file.write( f'Time spent in {result["name"]}: {sum([x["calcTime"] for x in result["taskSets"]]):.2e} -- Not schedulable: {result["notSchedulable"]}\n' )

print(f'Done.\nResults in TXT, CSV, PNG and PDF files with name root = {plotFileName}')