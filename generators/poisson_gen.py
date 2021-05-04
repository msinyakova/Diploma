import random
import numpy as np
import csv

poisson = np.random.poisson(0.7, 10)

np.savetxt("poisson.csv", poisson, delimiter=",")