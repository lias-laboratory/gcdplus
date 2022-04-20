from math import gcd, lcm, sqrt
from functools import reduce
from typing import Counter
from sys import exit
from os import path
from itertools import islice
from copy import deepcopy

# -----------------------------------------------------------
#create a list class without out of range
class ListClass(list):
    def __setitem__(self, index, value):
        self.extend([None] * ((max(index.start, index.stop - 1) if isinstance(index, slice) else index) - len(self) + 1))
        super().__setitem__(index, value)


# -----------------------------------------------------------
#Convert Nonetype of a list to zero
def f_None_Zero(list):
    List=[]
    for i in range(len(list)):
        if list[i] == None:
            List.append(0)
        else:
            List.append(list[i])
    return List

def lcm(a, b):
    return abs(a*b) // gcd(a, b)

def primeFactors(n: int):
    if n < 0:
        raise ValueError(f'Tried factoring {n} but input must be positive!')
    primes = [2, 3]
    factors = []
    if n % 2 == 0:
        factors.append(2)
        while n % 2 == 0:
            n /= 2
    prime = primes[1]
    while prime <= n:
        if n % prime == 0:
            factors.append(prime)
            while n % prime == 0:
                n /= prime
        else:
            isPrime = False
            while not isPrime:
                prime += 2
                isPrime = True
                for p in primes:
                    if prime % p == 0:
                        isPrime = False
                        break
    return tuple(factors)

# -----------------------------------------------------------
# Python program to print prime factors


# A function to print all prime factors of
# a given number n
def primeFactorsCount(n):
	
	# Print the number of two's that divide n
    List=[]
    while n % 2 == 0:
        List.append(2)
        #print(2)
        n = int(n / 2)
		
    # n must be odd at this point
    # so a skip of 2 ( i = i + 2) can be used
    for i in range(3,int(sqrt(n))+1,2):
		
        # while i divides n , print i ad divide n
        while n % i== 0:
            List.append(i)
            #print(i)
            n = int(n / i)
			
    # Condition if n is a prime
    # number greater than 2
    if n > 2:
        List.append(n)
        #print(n)
    c = Counter(List)
    c=list(c.items())
    #print('c : ',c)
    return c

print()
# This function's code is contributed by Harshit Agrawal




def calcNonEquivOffsets( listPeriods ):

    n = len(listPeriods)

    nonEquivOffsets = [0] * n

    currentLCM = 1
    for i in range(n):
        nonEquivOffsets[i] = gcd(listPeriods[i], currentLCM)
        currentLCM = lcm(currentLCM, listPeriods[i])

    return nonEquivOffsets