# 
# OFFSET ASSIGNMENT ANALYSIS
# 
# Compare Calculation Time and Delay Performance of different offset assignment strategies
#
# Developped by Yuri Hérouard
# LIAS (ISAE-ENSMA)

# -----------------------------------------------------------
# Input variables

input_xmlFileName = 'paparazzi_case3_tasks'     # WITHOUT EXTENTION - Name of the file containing the periods
outputFolderRoot = 'paparazziAnalysis'            # WITHOUT EXTENTION - Root for the name of the files containing the results

# filterSets = True                   # True | False -- Enable filtering task sets with large enough GCDs

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

verbose = False     # Print progress while doing analysis

optimTimeLimit = 10  # seconds


# -----------------------------------------------------------
# Import

from fractions import Fraction
from lxml import etree
from pathlib import Path
from time import time as now
from copy import deepcopy
from heapq import nlargest

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

def runSchedHeur(heuristicFunction, taskSet):

    start = now()
    offsets = heuristicFunction(taskSet)
    end = now()

    return {'calcTime': end - start, 'offsets': tuple(offsets)}
    

def runOptimAlgo(optimAlgorithm, taskSet, timeLimit=None):

    start = now()
    offsets = optimAlgorithm(taskSet, timeLimit_Sec=timeLimit)
    end = now()

    return {'calcTime': end - start, 'offsets': tuple(offsets)}


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



# -----------------------------------------------------------
# Pre-processing

inputFileName = input_xmlFileName + '.xml' 

baudrateList = [4800, 9600, 38400, 57600, 115200]   # bits/s (Standards: B4800, B9600, B38400, B57600, B115200)
headerSize = 8      # bytes
bitsPerByte = 10    # 8 + start + end bits  

# Manual insertion of sizes
sizes_bytes = [17, 58, 32, 15, 21, 11, 5, 20, 4, 28, 36, 57, 12, 12, 12, 12]
c = [(sizeBytes + headerSize) * bitsPerByte for sizeBytes in sizes_bytes]

# Reading XML
tree = etree.parse(inputFileName)
for i in range(len(baudrateList)):
    periodList = []
    okay = True
    for message in tree.xpath("/telemetry/process/mode/message"):
        # print(message.get("period"))
        p = Fraction(message.get("period")) * baudrateList[i]
        if message.get("period")=='0.062':
            p = Fraction(1/16) * baudrateList[i]
            print(message.get("name"), "-- 0.062 converted to 1/16")
        if not(float(p).is_integer()):
            print("Period = ", p ," is not an integer, baudrate = ", baudrateList[i], " cannot be used")
            okay = False
            break
        periodList.append(int(p))
    U = 0
    for j in range(len(periodList)): U += c[j] / periodList[j]
    if U > 1:
        print("U = ", U ," when baudrate = ", baudrateList[i], ", therefore it cannot be used.")
        okay = False
    if okay:
        baudrateUsed =  baudrateList[i]
        break

print()

print('Baud rate = ', baudrateUsed)
print('U = ', U)
print('Periods = ', periodList)
print('ExecTimes = ', c)

# periodList.reverse()
# c.reverse()

case_taskSet = [{'period':periodList[i], 'execTime':c[i]} for i in range(len(periodList))]
case_taskSet = tuple(case_taskSet)
# case_taskSet = tuple(case_taskSet[0:-1])

# Paparazzi-defined offsets
case_taskSet[9]['phase'] = 0
case_taskSet[10]['phase'] = 0
case_taskSet[11]['phase'] = 0

# outputFolder = outputFolderRoot 
Path(outputFolderRoot).mkdir(parents=True, exist_ok=False)

# ---------------------------------------------------------------------------------------
# Calculate offsets:

list_results = []

for algorithm in list_algorithms:

    if algorithm['name'] == 'Coupled Goossens\'s Heuristics':
        result_orig = {'name': 'Goossens\'s Heuristics (C)'}
        result_mod = {'name': 'Modified Goossens\'s Heuristics (C)'}
        
        coupledResult = runSchedHeur(algorithm['function'], case_taskSet)

        result_orig['calcTime'] = coupledResult['calcTime']
        result_mod['calcTime'] = coupledResult['calcTime']

        result_orig['offsets'] = coupledResult['offsets'][0]
        result_mod['offsets'] = coupledResult['offsets'][1]
        
        list_results.append( deepcopy(result_orig) )
        list_results.append( deepcopy(result_mod) )

        print(f"Time spent in {algorithm['name']} is: ", coupledResult['calcTime'])

    else:
        result = {}
        result['name'] = algorithm['name']

        if algorithm.get('optimization'): output = runOptimAlgo(algorithm['function'], case_taskSet, optimTimeLimit)
        else: output = runSchedHeur(algorithm['function'], case_taskSet)

        result['calcTime'] = output['calcTime']
        result['offsets'] = output['offsets']

        list_results.append( deepcopy(result) )
        print(f"Time spent in {result['name']} is: ", result['calcTime'])


# Save outputs to independent files !!!

# ---------------------------------------------------------------------------------------
# Get maximum delays from simulation

# !!! Import offsets ??

for result in list_results:
    maxDelays = getMaxDelaysFromSim(case_taskSet, [ O_i for O_i in result['offsets'] ] )
    result['maxDelays'] = tuple( maxDelays )


# Write brute results in txt file
with open(outputFolderRoot + '/results.txt', "w") as file:
    file.write('----------------- OUTPUT -----------------\n\n')
    file.write(f'Periods: {periodList}\n')
    file.write(f'ExecTimes: {c}\n\n')
    for result in list_results:
        file.write( f'{result["name"]}: ({result["calcTime"]:.2e})\n\n' )
        file.write( f'Offsets: {result["offsets"]}\n')
        file.write( f'Maximum delays: {result["maxDelays"]}\n\n')


functionNameList = tuple([result['name'] for result in list_results])

allMaxDelays = tuple( [ tuple( [y for y in result['maxDelays']] ) for result in list_results ] )

maxDelaysPerPeriod = tuple( [ tuple( [ result['maxDelays'][i]/case_taskSet[i]['period'] for i in range(len(case_taskSet)) ] ) for result in list_results ] )

maxDelaysPerExecTime = tuple( [ tuple( [
    result['maxDelays'][i] / nlargest(2, c)[1 if (i == c.index(max(c)) ) else 0]
    for i in range(len(case_taskSet)) ] ) for result in list_results ] )

maxDelaysOverDeadline = tuple( [ tuple( [
    (result['maxDelays'][i] - (case_taskSet[i]['period'] - case_taskSet[i]['execTime'])) if (result['maxDelays'][i] - (case_taskSet[i]['period'] - case_taskSet[i]['execTime']) > 0) else 0
    for i in range(len(case_taskSet)) ] ) for result in list_results ] )

# Plot in boxplot
# plotFileName = f'{outputFolder}/plot_{numberSets}x{numberTasks}t'
plotFileName = f'{outputFolderRoot}/plot'

printBoxplot4(functionNameList, allMaxDelays, maxDelaysPerPeriod, maxDelaysPerExecTime, maxDelaysOverDeadline, plotFileName)

print(f'Done.\nResults in TXT, CSV, PNG and PDF files with name root = {plotFileName}')