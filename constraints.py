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

    ### Add constraints ###

    ## No children next to the emergency exits
    emergency_seats = plane.emergency_seats
    for c in passengers.children:
        prob += lpSum([x[s][p] for s in emergency_seats for p in [c]]) == 0

    ## WCHR passengers
    alley_seats = plane.alley_seats
    for wchr in passengers.wchr:

        # WCHR are placed on the alleys
        prob += lpSum([x[s][p] for s in alley_seats for p in [wchr]]) == 1

        # WCHR freeze seats around them
        for s in plane.seats:
            neighs = plane.wchr_neigh[s]
            prob += lpSum([x[s][p] for s in neighs for p in passengers.passengers]) <= len(neighs) * (1 - x[s][wchr])

    ## WCHB passengers
    for wchb in passengers.wchb:
        for s in plane.seats:
            neighs = plane.wchb_neigh[s]
            prob += lpSum([x[s][p] for s in neighs for p in passengers.passengers]) <= len(neighs) * (1 - x[s][wchb])

    ## Business passengers
    for b in passengers.business:

        # Business passengers are placed on the business seats
        business_seats = plane.business_seats
        prob += lpSum([x[s][p] for s in business_seats for p in [b]]) == 1

        # Business passengers have no direct neighbors
        for s in business_seats:
            neighs = plane.business_neigh[s]
            prob += lpSum([x[s][p] for s in neighs for p in passengers.passengers]) <= len(neighs) * (1 - x[s][b])


    return None
