import numpy as np
import random
import math

def main():
    lam = 75

    expRV = []
    for i in range(1000):
    	expRV.append(float(-math.log(1 - random.uniform(0, 1))) / lam)

    print ("Mean: %f", (sum(expRV) / len(expRV)))
    print ("Variance: %f", np.var(expRV))


if __name__ == '__main__':
    main()
