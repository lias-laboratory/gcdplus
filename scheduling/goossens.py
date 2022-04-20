# 
# FIND OFFSETS OF TASKS
# 
# Developped by Matheus Ladeira
# Based on article: Goossens, Joël. "Scheduling of offset free systems." Real-Time Systems 24.2 (2003): 239-258.
# 
# Scheduling and simulation of non-preemptive periodic tasks with defined execution time.
# 
# -----------------------------------------------------------
# Import

from math import gcd
from random import randint

# -----------------------------------------------------------
# Goossens offset assignment heuristics

def goossensScheduling(list_tasks, verbose=False):
    
    n = len(list_tasks)

    list_periods = tuple( [ int(task['period']) for task in list_tasks ] )

    G = []
    for i in range(n):
        for j in range(i+1,n):
            G.append( (i, j, gcd(list_periods[i],list_periods[j])) )

    Gs = sorted(G, key=lambda element: element[2], reverse=True)

    if verbose:print('\nOffsets:')
    offsets = [0] * n
    mark = [False] * n
    k=0
    assignment = n
    while assignment > 0:
        Gs_k_row = Gs[k][0]
        Gs_k_col = Gs[k][1]
        Gs_k_gcd = Gs[k][2]
        if (not mark[Gs_k_col]) and (not mark[Gs_k_row]):
            offsets[Gs_k_row] = randint(0,list_periods[Gs_k_row]-1)
            offsets[Gs_k_col] = offsets[Gs_k_row] + Gs_k_gcd//2
            assignment = assignment -2
            mark[Gs_k_row] = True
            mark[Gs_k_col] = True
        elif not mark[Gs_k_col]:
            offsets[Gs_k_col] = offsets[Gs_k_row] + Gs_k_gcd//2
            assignment = assignment -1
            mark[Gs_k_col] = True
        elif not mark[Gs_k_row]:
            offsets[Gs_k_row] = offsets[Gs_k_col] + Gs_k_gcd//2
            assignment = assignment -1
            mark[Gs_k_row] = True
        k = k+1
    
    # Normalisation
    minOffset = min(offsets)
    for i in range(n): offsets[i] = (offsets[i] - minOffset) % list_periods[i]
    
    if verbose: print(offsets)
    
    return tuple(offsets)


# -----------------------------------------------------------
# Modified Goossens offset assignment heuristics 

def goossensModifiedScheduling(list_tasks, verbose=False):
    
    n = len(list_tasks)

    list_periods = tuple( [ int(task['period']) for task in list_tasks ] )
    list_execTimes = tuple( [ int(task['execTime']) for task in list_tasks ] )

    G = []
    for i in range(n):
        for j in range(i+1,n):
            G.append( (i, j, gcd(list_periods[i],list_periods[j])) )

    Gs = sorted(G, key=lambda element: element[2], reverse=True)

    if verbose:print('\nOffsets:')
    offsets = [0] * n
    mark = [False] * n
    k=0
    assignment = n
    while assignment > 0:
        Gs_k_row = Gs[k][0]
        Gs_k_col = Gs[k][1]
        Gs_k_gcd = Gs[k][2]
        if (not mark[Gs_k_col]) and (not mark[Gs_k_row]):
            offsets[Gs_k_row] = randint(0,list_periods[Gs_k_row]-1)
            offsets[Gs_k_col] = offsets[Gs_k_row] + (Gs_k_gcd + list_execTimes[Gs_k_row] - list_execTimes[Gs_k_col])//2
            assignment = assignment -2
            mark[Gs_k_row] = True
            mark[Gs_k_col] = True
        elif not mark[Gs_k_col]:
            offsets[Gs_k_col] = offsets[Gs_k_row] + (Gs_k_gcd + list_execTimes[Gs_k_row] - list_execTimes[Gs_k_col])//2
            assignment = assignment -1
            mark[Gs_k_col] = True
        elif not mark[Gs_k_row]:
            offsets[Gs_k_row] = offsets[Gs_k_col] + (Gs_k_gcd + list_execTimes[Gs_k_col] - list_execTimes[Gs_k_row])//2
            assignment = assignment -1
            mark[Gs_k_row] = True
        k = k+1

    # Normalisation
    minOffset = min(offsets)
    for i in range(n): offsets[i] = (offsets[i] - minOffset) % list_periods[i]

    if verbose:print(offsets)

    return tuple(offsets)



# -----------------------------------------------------------
# Couple original and modified Goossens offset assignment heuristics 

def goossensCoupledScheduling(list_tasks, verbose=False):
    n = len(list_tasks)

    list_periods = tuple( [ int(task['period']) for task in list_tasks ] )
    list_execTimes = tuple( [ int(task['execTime']) for task in list_tasks ] )

    G = []
    for i in range(n):
        for j in range(i+1,n):
            G.append( (i, j, gcd(list_periods[i],list_periods[j])) )

    Gs = sorted(G, key=lambda element: element[2], reverse=True)

    if verbose:print('\nOffsets:')
    offsets_orig = [0] * n
    offsets_mod = [0] * n
    mark = [False] * n
    k=0
    assignment = n
    while assignment > 0:
        Gs_k_row = Gs[k][0]
        Gs_k_col = Gs[k][1]
        Gs_k_gcd = Gs[k][2]
        if (not mark[Gs_k_col]) and (not mark[Gs_k_row]):
            offsets_orig[Gs_k_row] = randint(0,list_periods[Gs_k_row]-1)
            offsets_mod[Gs_k_row] = offsets_orig[Gs_k_row]
            offsets_orig[Gs_k_col] = offsets_orig[Gs_k_row] + Gs_k_gcd//2
            offsets_mod[Gs_k_col] = offsets_mod[Gs_k_row] + (Gs_k_gcd + list_execTimes[Gs_k_row] - list_execTimes[Gs_k_col])//2
            assignment = assignment -2
            mark[Gs_k_row] = True
            mark[Gs_k_col] = True
        elif not mark[Gs_k_col]:
            offsets_orig[Gs_k_col] = offsets_orig[Gs_k_row] + Gs_k_gcd//2
            offsets_mod[Gs_k_col] = offsets_mod[Gs_k_row] + (Gs_k_gcd + list_execTimes[Gs_k_row] - list_execTimes[Gs_k_col])//2
            assignment = assignment -1
            mark[Gs_k_col] = True
        elif not mark[Gs_k_row]:
            offsets_orig[Gs_k_row] = offsets_orig[Gs_k_col] + Gs_k_gcd//2
            offsets_mod[Gs_k_row] = offsets_mod[Gs_k_col] + (Gs_k_gcd + list_execTimes[Gs_k_col] - list_execTimes[Gs_k_row])//2
            assignment = assignment -1
            mark[Gs_k_row] = True
        k = k+1

    # Normalisation
    minOffset_orig = min(offsets_orig)
    for i in range(n): offsets_orig[i] = (offsets_orig[i] - minOffset_orig) % list_periods[i]
    minOffset_mod = min(offsets_mod)
    for i in range(n): offsets_mod[i] = (offsets_mod[i] - minOffset_mod) % list_periods[i]

    if verbose:
        print('Original: ', offsets_orig)
        print('Modified: ', offsets_mod)

    return (tuple(offsets_orig), tuple(offsets_mod))