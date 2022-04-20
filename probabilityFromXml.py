# 
# Calculate prime factors probabilities from XML file
# 
# Developped by Yuri Hérouard
# LIAS (ISAE-ENSMA)

# -----------------------------------------------------------
# Input Variables

input_xmlFileName = 'default_rotorcraft'    # File Name of the XML file defining message periods

baudrateList = [4800, 9600, 38400, 57600, 115200]     # bits/s (Standards: B4800, B9600, B38400, B57600, B115200)

# Variables to write matrix
writeMatrix = True      # Enable writing the factor matrix
grmax = 10      # Maximum granularity of the matrix


# -----------------------------------------------------------
# Import
from lxml import etree
import csv
from fractions import Fraction
from basicFunctions.toImport import *


# -----------------------------------------------------------
# Functions

def writeToCSV(filename, probabilities, primeList) :
    # Write probabilities into a csv file

    with open(filename+'.csv','w',newline='') as fichiercsv:
        writer = csv.writer(fichiercsv)
        writer.writerow(['Prime Factor', 'Power=0', 'Power=1', 'Power=2', 'Power=3', 'Power=4'])
        for i in range(len(probabilities)):
            writer.writerow([primeList[i]] + probabilities[i])

            

def writeMatrixToCSV(filename, M) :
    # Write period matrix into a csv file
    
    with open(filename + '.csv', 'w', newline='') as fichiercsv:
        writer = csv.writer(fichiercsv)
        for i in range(len(M)):
            writer.writerow(M[i])


def primeFactorsDistribution(listOfPeriods):
    # Probability count

    n=len(listOfPeriods)
    c=[]
    for i in range(len(listOfPeriods)):
        c+=primeFactorsCount(listOfPeriods[i])
    totalc=list(Counter(c).items()) # = [((Prime Factor, Power), Count), ... ]
    #print('(Prime Factor, Power), Count) : ',totalc)
    #sorted(c, key=lambda c: c[i])
    ListTup=[]
    for i in range(len(totalc)):
        prime=totalc[i][0][0]
        power=totalc[i][0][1]
        count=totalc[i][1]
        ListTup.append((prime,power,count))
    i=0
    #print(ListTup)
    ListTup=sorted(ListTup, key=lambda Tup: Tup[0])
    #print(ListTup)
    Weight=[]
    PrimeList=[]
    myiter = iter(range(0,len(ListTup)))
    j=0
    ListPower=ListClass([None])
    ListPower[ListTup[i][1]]=ListTup[i][2]
    for i in myiter:
        #print("i : ",i)
        ListPower[ListTup[i][1]]=ListTup[i][2]
        ii=i
        PrimeList.append(ListTup[i][0])
        prime=PrimeList[j]
        if ii<len(ListTup):
            while ii<len(ListTup) and prime==ListTup[ii][0]:
                #print("ii : ",ii)
                ListPower[ListTup[ii][1]]=ListTup[ii][2]
                if prime==(ListTup[ii+1][0] if ii+1 < len(ListTup) else None):
                    next(myiter, None)
                    ii+=1
                else :
                    break
        j+=1
        Weight.append(ListPower)
        ListPower=ListClass([None])
    for i in range(len(Weight)):
        Weight[i]=f_None_Zero(Weight[i])
        Weight[i][0]=n-sum(Weight[i])
    Proba=[]
    for i in range(len(Weight)):
        Proba.append([])
        for j in range(len(Weight[i])):
            Proba[i].append(Weight[i][j]/n)
    return PrimeList,Weight,Proba


def genMatrixFromProbabilities(probabilities, primeList, grmax):
    # Generate matrix from probabilities

    M = []
    for i in range(len(probabilities)):
        frac=[]
        Ldenom=[]
        Lnum=[]
        Lnumtest=[]
        denom=10
        for j in range(len(probabilities[i])):
            frac.append(Fraction(probabilities[i][j]).limit_denominator(grmax))
            f=frac[j].denominator
            Ldenom.append(f)
            Lnum.append(frac[j].numerator)
        denom=max(Ldenom)
        M.append([])
        Lnumtest=deepcopy(Lnum)
        Lnumtest.pop(0)
        if not(Lnum[0]==1 and f==1) or not(sum(Lnumtest)==0):
            #print(frac)
            for j in range(len(probabilities[i])):
                #occurrence=round(Proba[i][j]*denom)
                occurrence=round((frac[j].numerator/frac[j].denominator)*denom)
                for k in range(occurrence):
                    M[i].append(primeList[i]**j)
    return list(filter(lambda x: x, M))



# -----------------------------------------------------------
# Pre-prcessing

inputFileName = input_xmlFileName + '.xml' 

outputFileName = input_xmlFileName + '_rawProbDist'   # Output File Name of the probability csv file
if writeMatrix: outputFileNameMatrix = input_xmlFileName + '_xmlMatrix'     # Output File Name of the matrix's period file


# Reading XML

string_int = 0
p = 0
tree = etree.parse(inputFileName)
for i in range(len(baudrateList)):
    periodList = []
    okay = True
    baudrate_used = baudrateList[i]
    for message in tree.xpath("/telemetry/process/mode/message"):
        # print(message.get("period"))
        p = Fraction(message.get("period")) * baudrateList[i]
        if message.get("period")=='0.062':
            p=Fraction(1/16)*baudrateList[i]
            print(message.get("name"), "-- 0.062 converted to 1/16")
        periodList.append(p)
        if not(float(p).is_integer()):
            print("Period = ", p ," is not an integer, baudrate = ", baudrateList[i], " cannot be used")
            okay = False
            break
    if okay:
        break

print()

# -----------------------------------------------------------
# Processing

# Generate matrix from a randomly generated list of period 

primeList, weight, probability = primeFactorsDistribution(periodList)

print("Weight: ", weight)
print("Probability: ", probability)
print("PrimeList: ", primeList)
print("Baudrate used = ", baudrate_used)

writeToCSV(outputFileName, weight, primeList)

if writeMatrix:
    M = genMatrixFromProbabilities(probability,primeList,grmax)
    writeMatrixToCSV(outputFileNameMatrix,M)
print()