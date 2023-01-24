import pandas as pd
import numpy as np
from pulp import *
from planes import *
from passengers import *


def create_constraints(passengers, plane):

    # Problem
    prob = LpProblem("Passenger Seating Problem", LpMinimize)

    # Variables
    nb_p = len(passengers.passengers)
    nb_s = plane.nb_seat
    x = LpVariable.dict("x[i,j]", (range(1, nb_s+1), range(1, nb_p+1)), 0, 1)
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
        prob += lpSum([y[i,j] for i in range(first_element, last_element+1) for j in range(first_element, last_element+1)]) / 2

    ### CONSTRAINTS ###

    ## Children passengers
    emergency_seats = plane.emergency_seats
    for c in passengers.children:

        # No children next to the emergency exits
        prob += lpSum([x[s,c] for s in emergency_seats]) == 0

        # Children should have an adult next to them
        adults = passengers.men + passengers.women
        for s in plane.seats:
            neighs = plane.child_neigh[s]
            prob += lpSum([x[s,p] for s in neighs for p in adults]) >= x[s,c]

    ## WCHR passengers
    alley_seats = plane.alley_seats
    for wchr in passengers.wchr:

        # WCHR are placed on the alleys
        prob += lpSum([x[s,wchr] for s in alley_seats]) == 1

        # WCHR freeze seats around them
        prob += lpSum([x[s,wchr] for s in range(1,7)]) == 0
        print(plane.wchr_neigh)
        for s in plane.wchr_seats:
            neighs = plane.wchr_neigh[s]
            print('neighs: ', neighs)
            prob += lpSum([x[s,wchr] for s in neighs]) <= len(neighs) * (1 - x[s,wchr])

    ## WCHB passengers
    for wchb in passengers.wchb:
        
        prob += lpSum([x[s,wchb] for s in range(1,19)]) == 0
        for s in plane.wchb_seats:
            neighs = plane.wchb_neigh[s]
            prob += lpSum([x[s,wchb] for s in neighs]) <= len(neighs) * (1 - x[s,wchb])

    ## Business passengers
    for b in passengers.business:

        # Business passengers are placed on the business seats
        business_seats = plane.business_seats
        prob += lpSum([x[s,b] for s in business_seats]) == 1

        # Business passengers have no direct neighbors
        for s in business_seats:
            neighs = plane.business_neigh[s]
            prob += lpSum([x[s,p] for s in neighs for p in passengers.passengers]) <= len(neighs) * (1 - x[s,b])


    #Barycenter within the center zone
    xmin = plane.seat_position[plane.center_zone[0]][0]
    xmax = plane.seat_position[plane.center_zone[1]][0]
    ymin = plane.seat_position[plane.center_zone[0]][1]
    ymax = plane.seat_position[plane.center_zone[2]][1]
    x_barycenter = 1/nb_p * lpSum([x[s,p]*plane.seat_position[s][0]*passengers.mass[passengers.get_passenger_type(p)] for s in neighs for p in passengers.passengers])
    y_barycenter = 1/nb_p * lpSum([x[s,p]*plane.seat_position[s][1]*passengers.mass[passengers.get_passenger_type(p)] for s in neighs for p in passengers.passengers])
    prob +=  x_barycenter <= xmax
    prob +=  x_barycenter >= xmin
    prob +=  y_barycenter <= ymax
    prob +=  y_barycenter >= ymin
   
            
    ## Only one seat per passenger 
    for p in passengers.passengers:
        prob +=  lpSum([x[s,p] for s in plane.seats]) == 1
    
    ## Only one passenger per seat 
    for s in plane.seats:
        prob += lpSum([x[s,p] for p in passengers.passengers]) <= 1

    ## Constraints on y
    a = plane.a
    seats = plane.seats
    for group in Y.keys():
        group_passengers = passengers.bounds[group]
        y = Y[group]
        for p in group_passengers:
            for p_prime in group_passengers:

                prob += y[p,p_prime] >= lpSum([(x[s,p]- x[s,p_prime])*(a[s][0] + a[s][1]) for s in seats]) 
                prob += y[p,p_prime] >= lpSum([(x[s,p]- x[s,p_prime])*(a[s][0] - a[s][1]) for s in seats])
                prob += y[p,p_prime] >= lpSum([(x[s,p]- x[s,p_prime])*(-a[s][0] + a[s][1]) for s in seats])
                prob += y[p,p_prime] >= lpSum([(x[s,p]- x[s,p_prime])*(-a[s][0] - a[s][1]) for s in seats])

    ### SOLVE PROBLEM ###
    status = prob.solve()

    ### DISPLAY SOLUTION ###
    print(f'Optimal solution: {value(prob.objective)}')
    for s in plane.seats:
        for p in passengers.passengers:
            print(f'x[{s},{p}] = {x[s,p].varValue}')
