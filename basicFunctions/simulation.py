# 
# TASK EXECUTION SIMULATION
# 
# Developped by Matheus Ladeira
# LIAS (ISAE-ENSMA)
# 
# Scheduling and simulation of non-preemptive periodic tasks with defined execution time.


# -----------------------------------------------------------
# Import
from math import lcm, gcd
from functools import reduce
from time import time as now
from datetime import datetime, timedelta

# -----------------------------------------------------------
# Definitions

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
        # Print Newoffsets[i] on Complete
    if iteration == total: 
        print()


# -----------------------------------------------------------
# Simulate to get maximum delays

def getMaxDelaysFromSim(taskSet, offsets):

    n = len(taskSet)
    hyperperiod = reduce(lcm, [task['period'] for task in taskSet])
    maxTime = 2 * hyperperiod + max(offsets)

    maxDelays = [0] * n

    calls = list(offsets)

    # Start at the first call
    t = min(calls)
    while t < maxTime :
        # FIFO: check next task to be executed
        earliestCall = min(calls)
        i = calls.index(earliestCall)
        executingTask = taskSet[i]
        # Chech if there is any delay. If so, register.
        if earliestCall < t :
            delayTime = t - earliestCall
            maxDelays[i] = max(maxDelays[i], delayTime)
        # Else: forward to earliest call
        else:
            t = earliestCall

        # Execute task
        t += executingTask['execTime']

        # Update calls
        calls[i] += executingTask['period']

    return tuple(maxDelays)


# # -----------------------------------------------------------
# # Simulation

# def simulateTasks (executionTimes, periods, offsets, maxTime, printProgress = True, verbose = False, printResults = True):

#     offsetsCopy = list.copy(offsets)
#     if verbose: printProgress = False

#     n = len(executionTimes)
#     if (len(periods) != n) or (len(offsets) != n):
#         raise Exception("Input vectors must be consistent!")

#     if printResults: print('\nSIMULATION')

#     # Tuple of task tuples
#     if printResults:print('\nTask: U (c, P, O)')
#     tasks = []
#     for i in range(n):
#         taskTuple = (executionTimes[i], periods[i], offsets[i])
#         tasks.append(taskTuple)
#         if printResults:print(f'{i}:\t{100*executionTimes[i]/periods[i]:.2f}%\t{taskTuple}')
#     tasks = tuple(tasks)

#     maxDelays = [0] * n
#     sumDelays = [0] * n
#     calls = offsets.copy()

#     # print(offsets)
#     t = min(calls)

#     if verbose : print(f'Starting at {t} ticks.')

#     while t < maxTime :

#         if printProgress: printProgressBar(t, maxTime, prefix = 'Progress:', suffix = 'Complete', decimals = 8, length = 50)

#         earliestCall = min(calls)
#         currentTaskIndex = calls.index(earliestCall)

#         if verbose: print(f'Earliest call is {earliestCall}, from task {currentTaskIndex}.')
        
#         if earliestCall < t :
#             delayTime = t - earliestCall
#             sumDelays[currentTaskIndex] += delayTime
#             maxDelays[currentTaskIndex] = max(maxDelays[currentTaskIndex], delayTime)
#             if verbose: print(f'There has been a delay of {delayTime}. Max delay value for this task is {maxDelays[currentTaskIndex]}')
#         else:
#             t = earliestCall

#         t += tasks[currentTaskIndex][0]
#         if verbose: print(f'Added {tasks[currentTaskIndex][0]} to current time, which is now {t}.')

#         calls[currentTaskIndex] += tasks[currentTaskIndex][1]
#         if verbose: print(f'Next task call will be in t = {calls[currentTaskIndex]}.')

#     if printProgress: 
#         print(' '*100, end = '\r')
#         printProgressBar(1, 1, prefix = 'Progress:', suffix = 'Complete', decimals = 0, length = 50)

#     '''print('\nGeneral statistics:')
#     print('(Task: mean delay (relative value) | max delay (relative value))')
#     for i in range(n) : print(f'{i}: {sumDelays[i]*tasks[i][1]/maxTime:.2f} ({sumDelays[i]*100/maxTime:.2f}%)| {maxDelays[i]} ({100*maxDelays[i]/tasks[i][1]:.2f}%)')
#     print(f'Overall: {sum(sumDelays)} ({sum(sumDelays)*100/maxTime:.2f}%)| {sum(maxDelays)} ({100*sum(maxDelays)/sum(periods):.2f}%)')'''
#     if printResults: f_printResults(n, sumDelays, maxDelays, maxTime, periods)

#     return maxDelays


# -----------------------------------------------------------
# Print Simulation Results

def f_printResults(n, sumDelays, maxDelays, maxTime, periods):
    print('\nGeneral statistics:')
    print('(Task: mean delay (relative value) | max delay (relative value))')
    for i in range(n) : print(f'{i}: {sumDelays[i]*periods[i]/maxTime:.2f} ({sumDelays[i]*100/maxTime:.2f}%)| {maxDelays[i]} ({100*maxDelays[i]/periods[i]:.2f}%)')
    print(f'Overall: {sum(sumDelays)} ({sum(sumDelays)*100/maxTime:.2f}%)| {sum(maxDelays)} ({100*sum(maxDelays)/sum(periods):.2f}%)')
    return


# -----------------------------------------------------------
# Simulation specific for eval best setup

def evalOffsetAssignment(taskSet, offsets, previousMax = None):

    n = len(taskSet)
    list_periods = [task['period'] for task in taskSet]

    maxDelays = [0] * n
    hyperperiod = reduce(lcm, list_periods)
    maxTime = 2*hyperperiod + max(offsets)

    calls = list(offsets)
    t = min(calls)
    while t < maxTime :
        earliestCall = min(calls)
        i = calls.index(earliestCall)
        currentTask = taskSet[i]
        
        if earliestCall < t :
            delayTime = t - earliestCall
            delayTime_T = delayTime / currentTask['period']
            if (previousMax != None) and (delayTime_T > previousMax): return None
            maxDelays[i] = max(maxDelays[i], delayTime_T)
        else:
            t = earliestCall

        t += currentTask['execTime']
        calls[i] += currentTask['period']

    return max(maxDelays)


# -----------------------------------------------------------
# Evaluate the setup that has the best results with the Simulation

def countPossibilities(listPeriods):

    nPossibilities = 1
    consideredPeriods = []
    consideredPeriods.append(listPeriods[0])

    n = len(listPeriods)
    for i in range(1, n):
        nPossibilities *= gcd(listPeriods[i], reduce(lcm, consideredPeriods))
        consideredPeriods.append(listPeriods[i])

    return nPossibilities


def evalBestSetup(taskSet, generator_offsetsAssignments):

    bestAssignment = list(next(generator_offsetsAssignments))
    bestResult = evalOffsetAssignment(taskSet, bestAssignment)

    n = countPossibilities([task['period'] for task in taskSet])
    i = 1

    start = now()
    for assignment in generator_offsetsAssignments:

        localResult = evalOffsetAssignment(taskSet, list(assignment), bestResult)

        i += 1
        
        if i == 100000:
            print(f'{datetime.now().strftime("%H:%M:%S")} | {i}/{n} Expected remaining time = {timedelta(seconds=(now() - start)*(n - i)/i)}')

        if localResult != None:
            if localResult == 0:
                bestAssignment = list(assignment)
                return bestAssignment
            else:
                bestResult = localResult
                bestAssignment = list(assignment)

    return tuple(bestAssignment) # return offset assignment (less sumDelay, less MaxDelay)