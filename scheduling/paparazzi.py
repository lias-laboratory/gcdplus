# 
# FIND OFFSETS OF TASKS
# 
# Scheduling of non-preemptive periodic tasks with defined execution time.
# 
# Developped by ENAC

def paparazziScheduling(listTasks, verbose = False):

    n = len(listTasks)
    offsets = [0] * n

    list_periods = tuple( [ int(task['period']) for task in listTasks ] )

    k = 0
    for i in range(n):
        if not ('phase' in listTasks[-1-i]):
            offsets[-1-i] = int( k * list_periods[-1-i] / 10 )
            k = (k + 1) % 10
        else:
            offsets[-1-i] = listTasks[-1-i]['phase'] * list_periods[-1-i]

    return tuple( offsets )
