import random
import math

def poisson(lambd,k):
    e=2.71828 # This is the math constant e
    return ((lambd**k)*(e**(0.0-lambd)))/math.factorial(k)

def poisson_sample(lambd):
    thresh = random.random()
    p=0.0
    for x in range(25):
        p += poisson(lambd,x)
        if p >= thresh:
            return x