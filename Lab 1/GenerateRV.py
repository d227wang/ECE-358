#!/usr/bin/env python3
import numpy as np
import random
import math

###############################################################################
# Create exponential random variables
# Functions: 
# generateRV(lam) - Takes in lam as the rate parameter and returns a exponential
#                    random Variable
# generateRVArray(lam, len) - generates an array of length len of exponential
#                             random variables with rate parameter lam
#
###############################################################################

def generateRVArray(lam, len):
    expRV = np.zeros(len)
    for i in range(len):
    	expRV[i] = (float(-math.log(1 - random.uniform(0, 1))) / lam)
    return expRV

def generateRV(lam):
    #Use of inverse method to generate exponential random variable as given in lab manual
	expRV = (float(-math.log(1 - random.uniform(0, 1))) / lam)
	return expRV

# Test of random variable functions
def main():
	
    lam = 75

    expRV = generateRVArray(lam, 1000)

    expectedMean = 1/75
    mean = sum(expRV) / len(expRV)

    expectedVar = expectedMean**2
    var = np.var(expRV)
    print ("Expected Mean:", expectedMean)
    print ("Mean: ", mean)
    print ("% difference:", 100*(mean - expectedMean)/expectedMean)

    print ("Expected Variance:", expectedVar)
    print ("Variance: %f", var)
    print ("% difference:", 100*(var - expectedVar)/expectedVar)


if __name__ == '__main__':
    main()