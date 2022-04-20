# 
# FIND OFFSETS OF TASKS
# 
# Scheduling and simulation of non-preemptive periodic tasks with defined execution time.
# 
# Developped by Matheus Ladeira
# LIAS (ISAE-ENSMA)


# -----------------------------------------------------------
# Import

from basicFunctions.toImport import *
from time import time as now


def heuristicScheduling(listTasks, verbose = False):

    n = len(listTasks)

    list_periods = tuple( [ int(task['period']) for task in listTasks ] )
    list_execTimes = tuple( [ int(task['execTime']) for task in listTasks ] )

    overallGCD = reduce(gcd, list_periods)
    
    subperiods = tuple( [ int(period // overallGCD) for period in list_periods ] )

    # -----------------------------------------------------------
    # Offset calculation

    # Create vector/tuple with task information: i, c, Ts, primes, 
    # Order as: increasing subperiod, decreasing execution time / length
    reorderedTasks = [(i, list_execTimes[i], subperiods[i], primeFactors(subperiods[i])) for i in range(n)]
    reorderedTasks = sorted(reorderedTasks, key=lambda task: (task[2], -task[1], task[0]), reverse=False)

    # Result vector: [Oh, Og, Oa, sum]
    offsets = [[] for _ in range(n)]

    # Count potential Transaction Groups (total number of prime factors [+1])
    primeSections = set()
    for task in reorderedTasks:
        if task[2] == 1: primeSections.add(1)
        for p in task[3]: primeSections.add(p)
    primeSections = tuple(primeSections)

    sectionSizes = [0] * len(primeSections)
    assignedTasks = [[] for _ in primeSections]

    # For every task inside the task list:
    for task in reorderedTasks:
        taskIndex = task[0]
        taskExecutionTime = task[1]
        taskSubperiod = task[2]
        taskPrimes = task[3]
        number_taskPrimes = len(taskPrimes)
        # print(f'Assigning offset to task {taskIndex}: ({taskExecutionTime}, {taskSubperiod}). Primes: {taskPrimes}')

        # Create #nPrimes vectors of size Ts + vector of size nPrimes
        busyTimes = [[0] * taskSubperiod for _ in range(number_taskPrimes)]
        sectionMinBusyTimes = [0] * number_taskPrimes
        delta_sectionSize = [0] * number_taskPrimes

        for primeOption in range(number_taskPrimes):
            # Get the partition indexes
            sectionIndex = primeSections.index(taskPrimes[primeOption])
            # print(f'Evaluating partition {partitionIndex} (p = {taskPrimes[primeOption]})...')

            # For every already assigned task in the partition:
            for task_i in assignedTasks[sectionIndex]:
                # Get busy time
                Ci = list_execTimes[task_i]
                Oai = offsets[task_i][2]
                tBusy = Ci + Oai
                # Compare to values in indexes congruent to Ohi in mod GCD(Tsi, Ts)
                Tsi = subperiods[task_i]
                gcdBetweenTasks = gcd(Tsi, taskSubperiod)
                osiModGCD = offsets[task_i][0] % gcdBetweenTasks
                # print(f'Interference with task {task_i}: ({Ci}, {Tsi}). Oh = {offsets[task_i][0]}, congruent to {osiModGCD} (mod {gcdBetweenTasks})')

                while osiModGCD < taskSubperiod:
                    if busyTimes[primeOption][osiModGCD] < tBusy: busyTimes[primeOption][osiModGCD] = tBusy
                    osiModGCD += gcdBetweenTasks
                # print(f'New interference vector for option {primeOption}: {busyTimes[primeOption]}')

            # Get respective smallest values
            sectionMinBusyTimes[primeOption] = min(busyTimes[primeOption])

            # Calculate possible delta in partition length
            tBusyThisSection = sectionMinBusyTimes[primeOption] + taskExecutionTime
            currentSectionSize = sectionSizes[sectionIndex]
            delta_sectionSize[primeOption] = max(currentSectionSize, tBusyThisSection) - currentSectionSize
            # print(f'Minimum = {partitionMinBusyTimes[primeOption]} --> New busy period would be {tBusyThisPartition}. Current partition size is {currenttransactionGroupsize}. Delta = {deltatransactionGroupsize[primeOption]}')

        # Decide partition:
        if number_taskPrimes == 0:
            chosenSection = 0
            Oa = sectionSizes[chosenSection]
            Oh = 0
            chosenPrime = 1
            desiredDeltaSize = taskExecutionTime
        else:
            desiredDeltaSize = min(delta_sectionSize)
            chosenIndex = delta_sectionSize.index(desiredDeltaSize)
            chosenPrime = taskPrimes[chosenIndex]
            chosenSection = primeSections.index(chosenPrime)

            # Assign Subperiod Offset (Oh * GCD) and Additional Offset (Oa)
            Oa = sectionMinBusyTimes[chosenIndex]
            new_var = busyTimes[chosenIndex]
            Oh = new_var.index(Oa)

        offsets[taskIndex] = [0] * 4
        offsets[taskIndex][0] = Oh
        offsets[taskIndex][2] = Oa

        # Update partition size
        tBusyFinal = Oa + taskExecutionTime
        sectionSizes[chosenSection] = max(sectionSizes[chosenSection], tBusyFinal)
        assignedTasks[chosenSection].append(taskIndex)

        # print(f'Assigned to partition {chosenPartition} (p = {chosenPrime}) with Oh = {Oh}, Oa = {Oa}. Added {desiredDeltaSize} to partition size.\n')

    # Assign Transaction Group offsets (Og)
    k = 0
    Og = 0
    for tasksInPartition in assignedTasks:
        if tasksInPartition != []:
            for task in tasksInPartition: offsets[task][1] = Og
        Og += sectionSizes[k]
        k += 1

    # Sum offsets
    if verbose:
        print('\nOFFSETS')
        print('\ni \tOh \tOg \tOa \tO')
    for i in range(n):
        offsets[i][3] =  offsets[i][0] * overallGCD + offsets[i][1] + offsets[i][2]
        if verbose: print(f'{i}:\t{offsets[i][0]}\t{offsets[i][1]}\t{offsets[i][2]}\t{offsets[i][3]}')

    if verbose:
        print('\nTransaction Groups and their sizes (bits)')
        sumTransactionGroups = sum(sectionSizes)
        for i in range(len(primeSections)):
            print(f'{primeSections[i]}: {sectionSizes[i]}')
        print(f'Sum: {sumTransactionGroups} bits')
        if sumTransactionGroups > overallGCD: print(f'Expected delay of {sumTransactionGroups - overallGCD} bits')
        else: print(f'Free time of at least {overallGCD - sumTransactionGroups} bits per hypertick')

    finalOffsets = [line[3] for line in offsets]
    return tuple(finalOffsets)

    
def heuristicScheduling2(taskSet, verbose = False):

    taskSet = [task for task in taskSet]

    n = len(taskSet)
    overallGCD = reduce(gcd, [ int(task['period']) for task in taskSet ])

    for i in range(n):
        taskSet[i]['i'] = i
        taskSet[i]['subperiod'] = int(taskSet[i]['period'] // overallGCD)
        taskSet[i]['primeFactors'] = primeFactors(taskSet[i]['subperiod'])


    # list_periods = tuple( [ int(task['period']) for task in taskSet ] )
    # list_execTimes = tuple( [ int(task['execTime']) for task in taskSet ] )
    # subperiods = tuple( [ int(period // overallGCD) for period in list_periods ] )

    # -----------------------------------------------------------
    # Offset calculation

    # Create vector/tuple with task information: i, c, Ts, primes, 
    # Order as: increasing subperiod, decreasing execution time / length
    # reorderedTasks = [{'i': i, 'execTime': taskSet[i]['execTime'], 'subperiod': subperiods[i], 'primeFactors': primeFactors(subperiods[i])} for i in range(n)]
    reorderedTasks = sorted(taskSet, key=lambda task: (task['subperiod'], -task['execTime'], task['i']), reverse=False)

    # Result vector: [Oh, Og, Oa, sum]
    offsets = [[] for _ in range(n)]

    # Count potential Transaction Groups (total number of prime factors [+1])
    primeSections = set()
    for task in reorderedTasks:
        if task['subperiod'] == 1: primeSections.add(1)
        for p in task['primeFactors']: primeSections.add(p)
    primeSections = tuple(primeSections)

    sectionSizes = [0] * len(primeSections)
    assignedTasks = [[] for _ in primeSections]

    # For every task inside the task list:
    for task in reorderedTasks:
        taskIndex = task['i']
        taskExecutionTime = task['execTime']
        taskSubperiod = task['subperiod']
        taskPrimes = task['primeFactors']
        number_taskPrimes = len(taskPrimes)

        # Create #nPrimes vectors of size Ts + vector of size nPrimes
        busyTimes = [[0] * taskSubperiod for _ in range(number_taskPrimes)]
        sectionMinBusyTimes = [0] * number_taskPrimes
        delta_sectionSize = [0] * number_taskPrimes

        for primeOption in range(number_taskPrimes):

            # Get the partition indexes
            sectionIndex = primeSections.index(taskPrimes[primeOption])

            # For every already assigned task in the partition:
            for task_i in  [sectionIndex]:

                # Get busy time
                Ci = taskSet[task_i]['execTime']
                Oai = offsets[task_i][2]
                tBusy = Ci + Oai

                # Compare to values in indexes congruent to Ohi in mod GCD(Tsi, Ts)
                Tsi = taskSet[task_i]['subperiod']
                gcdBetweenTasks = gcd(Tsi, taskSubperiod)
                osiModGCD = offsets[task_i][0] % gcdBetweenTasks

                while osiModGCD < taskSubperiod:
                    if busyTimes[primeOption][osiModGCD] < tBusy: busyTimes[primeOption][osiModGCD] = tBusy
                    osiModGCD += gcdBetweenTasks

            # Get respective smallest values
            sectionMinBusyTimes[primeOption] = min(busyTimes[primeOption])

            # Calculate possible delta in partition length
            tBusyThisSection = sectionMinBusyTimes[primeOption] + taskExecutionTime
            currentSectionSize = sectionSizes[sectionIndex]
            delta_sectionSize[primeOption] = max(currentSectionSize, tBusyThisSection) - currentSectionSize

        # Decide partition:
        if number_taskPrimes == 0:
            chosenSection = 0
            Oa = sectionSizes[chosenSection]
            Oh = 0
            chosenPrime = 1
            desiredDeltaSize = taskExecutionTime
        else:
            desiredDeltaSize = min(delta_sectionSize)
            chosenIndex = delta_sectionSize.index(desiredDeltaSize)
            chosenPrime = taskPrimes[chosenIndex]
            chosenSection = primeSections.index(chosenPrime)

            # Assign Subperiod Offset (Oh * GCD) and Additional Offset (Oa)
            Oa = sectionMinBusyTimes[chosenIndex]
            new_var = busyTimes[chosenIndex]
            Oh = new_var.index(Oa)

        offsets[taskIndex] = [0] * 4
        offsets[taskIndex][0] = Oh
        offsets[taskIndex][2] = Oa

        # Update sextion size
        tBusyFinal = Oa + taskExecutionTime
        sectionSizes[chosenSection] = max(sectionSizes[chosenSection], tBusyFinal)
        assignedTasks[chosenSection].append(taskIndex)

    # Assign Transaction Group offsets (Og)
    k = 0
    Og = 0
    for tasksInPartition in assignedTasks:
        if tasksInPartition != []:
            for task in tasksInPartition: offsets[task][1] = Og
        Og += sectionSizes[k]
        k += 1

    # Sum offsets
    if verbose:
        print('\nOFFSETS')
        print('\ni \tOh \tOg \tOa \tO')
    for i in range(n):
        offsets[i][3] =  offsets[i][0] * overallGCD + offsets[i][1] + offsets[i][2]
        if verbose: print(f'{i}:\t{offsets[i][0]}\t{offsets[i][1]}\t{offsets[i][2]}\t{offsets[i][3]}')

    if verbose:
        print('\nTransaction Groups and their sizes (bits)')
        sumTransactionGroups = sum(sectionSizes)
        for i in range(len(primeSections)):
            print(f'{primeSections[i]}: {sectionSizes[i]}')
        print(f'Sum: {sumTransactionGroups} bits')
        if sumTransactionGroups > overallGCD: print(f'Expected delay of {sumTransactionGroups - overallGCD} bits')
        else: print(f'Free time of at least {overallGCD - sumTransactionGroups} bits per hypertick')

    finalOffsets = [line[3] for line in offsets]
    return tuple(finalOffsets)