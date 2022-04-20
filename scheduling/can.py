# 
# FIND OFFSETS OF TASKS
# 
# Scheduling and simulation of non-preemptive periodic tasks with defined execution time.
# 
# Grenier, Mathieu, Lionel Havet, and Nicolas Navet. "Pushing the limits of CAN-scheduling frames with offsets provides a major performance boost." 4th European Congress on Embedded Real Time Software (ERTS 2008). 2008.


def CANScheduling(list_tasks, verbose=False):

    list_periods = tuple( [ int(task['period']) for task in list_tasks ] )

    calls = []
    assignedOffsets = []
    assignedTasks = []

    maxPeriod = max(list_periods)

    for task in list_tasks:
        taskPeriod = task['period']
        calls = reduceIfFull(calls, maxPeriod)
        newOffset = middleOfLargestInterval(calls, maxPeriod) % taskPeriod
        assignedOffsets.append(newOffset)
        assignedTasks.append(task)
        calls = addToCalls(calls, newOffset, taskPeriod, maxPeriod)

    return tuple(assignedOffsets)


# ----------------------
# Auxiliary functions

def reduceIfFull(listCalls, maximum):
    full = True
    i = 0
    for i in range(maximum):
        if not (i in listCalls) :
            full = False
            break
    if full:
        for i in range(maximum): listCalls.remove(i)
        return reduceIfFull(listCalls, maximum)
    return listCalls


def middleOfLargestInterval(listCalls, maxTime):
    if len(listCalls) == 0: return (maxTime -1)//2
    if listCalls[0] == 0: position = 0
    else: position = (listCalls[0] - 1) // 2
    maxInterval = listCalls[0]

    for i in range(len(listCalls)-1):
        delta = listCalls[i+1] - listCalls[i]
        if delta > maxInterval:
            maxInterval = delta
            position = listCalls[i] + delta//2    # Add 0 if delta = 1 or 2; add 1 if biggestInterval_length = 3 or 4; ...
    delta = maxTime - 1 - listCalls[-1]

    if delta > maxInterval: return listCalls[-1] + (delta - 1)//2
    else: return position


def addToCalls(calls, offset, period, maximum):
    offset = offset % period
    i = offset
    while i < maximum:
        calls.append(i)
        i += period
    calls.sort()
    return calls
