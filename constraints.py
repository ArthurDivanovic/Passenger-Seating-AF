import pandas as pd
import numpy as np
from pulp import *
from planes import *
from passengers import *


def create_constraints(passengers, plane):

    # Problem
    prob = LpProblem("Passenger Seating Problem", LpMinimize)

    # Variables
    p = len(passengers.passengers)
    s = plane.nb_seat
    x = LpVariable.dict("x[i,j]", (range(1, s+1), range(1, p+1)), 0, 1)
    Y = dict()
    for group in passengers.bounds.keys():
        first_element = passengers.bounds[group][0]
        last_element = passengers.bounds[group][1]
        Y[group] = LpVariable.dict("y"+str(group)+"[i,j]", (range(first_element, last_element+1), range(first_element, last_element+1)), 0, None)

    # Objective function
    for group in Y.keys():
        y = Y[group]
        first_element = passengers.bounds[group][0]
        last_element = passengers.bounds[group][1]
        group_size = np.array(y).shape[0]
        prob += lpSum([y[i][j] for i in range(first_element, last_element+1) for j in range(first_element, last_element+1)]) / 2

    # Add constraints
    for p in passengers.passengers:
        prob +=  sum(x[:,p]) == 1
    
    for s in plane.seats:
        prob += sum(x[s,:]) <= 1
    
    

    return None
