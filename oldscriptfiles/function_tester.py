from time import perf_counter
import math
import numpy as np

def abolute(x):
    return 0 if abs(x) == 0 else x / abs(x)

def ifstatement(x):
    if x >0: return 1
    elif x == 0: return 0
    else: return -1

def comp(x):
    return (x > 0) - (x < 0)

def mathmodule(x):
    return math.copysign(1, x)

def npmodule(x):
    return np.sign(x)

t1_start = perf_counter()

for i in range(-10000,10000):
    abolute(100)

t1_stop = perf_counter()
print(t1_stop-t1_start)
