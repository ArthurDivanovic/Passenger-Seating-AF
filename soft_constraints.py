import pandas as pd
import numpy as np
from pulp import *
from planes import *
from passengers import *
import matplotlib.pyplot as plt
import gurobipy
import time 


def soft_gurobi_solving(passengers, plane, time_limit=300, alpha=0, mip_gap=0, callback=False):

    # Model
    model = gurobipy.Model("Passenger Seating Problem")

    ## Variables ##

    nb_p = len(passengers.passengers)
    nb_s = plane.nb_seat
    total_mass = sum([passengers.mass[passengers.get_passenger_type(p)] for p in passengers.passengers])
    x = {(i, j): model.addVar(vtype=gurobipy.GRB.BINARY, name="x[i,j]") for i in range(1, nb_s+1) for j in range(1, nb_p+1)}
    Y = dict()
    for group in passengers.bounds.keys():
        first_element = passengers.bounds[group][0]
        last_element = passengers.bounds[group][1]
        Y[group] = {(i, j): model.addVar(name="y"+str(group)+"[i,j]") for i in range(first_element, last_element+1) for j in range(first_element, last_element+1)}
    # Gap variables for constraint: "Children should have an adult next to them"
    eps1 = dict()
    for c in passengers.children:
        eps1[c] = model.addVar(lb=0, vtype=gurobipy.GRB.CONTINUOUS, name="eps1[c]")
    # Gap variables for constraint: "Children are not placed near emergency exits"
    eps2 = dict()
    for c in passengers.children:
        eps2[c] = model.addVar(lb=0, vtype=gurobipy.GRB.CONTINUOUS, name="eps2[c]")
 
    

    ### CONSTRAINTS ###

    ## Only one seat per passenger 
    for p in passengers.passengers:
        model.addConstr(sum([x[s,p] for s in plane.seats]) == 1)
    
    ## Only one passenger per seat 
    for s in plane.seats:
        model.addConstr(sum([x[s,p] for p in passengers.passengers]) <= 1)

    ## Constraints on y
    a_u3 = plane.a_u3
    a_l3 = plane.a_l3
    seats = plane.seats
    for group in Y.keys():
        group_passengers = passengers.bounds[group]
        y = Y[group]
        if group_passengers[1] - group_passengers[0] <= 3:
            a = a_l3
        else:
            a = a_u3
        for p in range(group_passengers[0],group_passengers[1]+1):
            for p_prime in range(group_passengers[0],group_passengers[1]+1): 

                model.addConstr(y[p,p_prime] >= sum([(x[s,p]- x[s,p_prime])*(a[s][0] + a[s][1]) for s in seats]))
                model.addConstr(y[p,p_prime] >= sum([(x[s,p]- x[s,p_prime])*(a[s][0] - a[s][1]) for s in seats]))
                model.addConstr(y[p,p_prime] >= sum([(x[s,p]- x[s,p_prime])*(-a[s][0] + a[s][1]) for s in seats]))
                model.addConstr(y[p,p_prime] >= sum([(x[s,p]- x[s,p_prime])*(-a[s][0] - a[s][1]) for s in seats]))

    ## Barycenter within the center zone
    xmin = plane.seat_position[plane.center_zone[0]][0]
    xmax = plane.seat_position[plane.center_zone[1]][0]
    ymin = plane.seat_position[plane.center_zone[0]][1]
    ymax = plane.seat_position[plane.center_zone[2]][1]
    x_barycenter = 1/total_mass * sum([x[s,p]*plane.seat_position[s][0]*passengers.mass[passengers.get_passenger_type(p)] for s in seats for p in passengers.passengers])
    y_barycenter = 1/total_mass * sum([x[s,p]*plane.seat_position[s][1]*passengers.mass[passengers.get_passenger_type(p)] for s in seats for p in passengers.passengers])
    model.addConstr(1/total_mass * sum([x[s,p]*plane.seat_position[s][0]*passengers.mass[passengers.get_passenger_type(p)] for s in seats for p in passengers.passengers]) <= xmax)
    model.addConstr(1/total_mass * sum([x[s,p]*plane.seat_position[s][0]*passengers.mass[passengers.get_passenger_type(p)] for s in seats for p in passengers.passengers]) >= xmin)
    model.addConstr(1/total_mass * sum([x[s,p]*plane.seat_position[s][1]*passengers.mass[passengers.get_passenger_type(p)] for s in seats for p in passengers.passengers]) <= ymax)
    model.addConstr(1/total_mass * sum([x[s,p]*plane.seat_position[s][1]*passengers.mass[passengers.get_passenger_type(p)] for s in seats for p in passengers.passengers]) >= ymin)

    ## Business Passengers
    business_passengers = len(passengers.business)
    business_rows = (business_passengers // 4) if business_passengers%4==0 else (business_passengers // 4 + 1)
    business_seats = [i for i in range(1, business_rows * 6 + 1)]
    for b in passengers.business:
        # Business passengers must be attributed to a business seat 
        model.addConstr(sum([x[s,b] for s in business_seats]) == 1)
        
        # Business passengers don't have neighbors
        for s in business_seats:
            neighs = plane.business_neigh[s]
            model.addConstr(sum([x[s,p] for s in neighs for p in passengers.passengers]) <= len(neighs) * (1 - x[s,b]))

    # No economy passengers in the business seats
    for eco in passengers.economy:
        model.addConstr(sum([x[s,eco] for s in business_seats]) == 0)

    ## Children passengers
    emergency_seats = plane.emergency_seats
    for c in passengers.children:

        # No children next to the emergency exits
        model.addConstr(sum([x[s,c] for s in emergency_seats]) == eps2[c])

        # Children should have an adult next to them
        adults = passengers.men + passengers.women
        for s in plane.seats:
            neighs = plane.child_neigh[s]
            model.addConstr(sum([x[s,p] for s in neighs for p in adults]) >= x[s,c] - eps1[c])

    ## WCHR passengers
    wchr_seats = plane.wchr_seats
    for wchr in passengers.wchr:

        # WCHR are placed on the alleys
        model.addConstr(sum([x[s,wchr] for s in wchr_seats]) == 1)

        # WCHR freeze seats around them
        for s in wchr_seats:
            neighs = plane.wchr_neigh[s]
            model.addConstr(sum([x[s,p] for s in neighs for p in passengers.passengers]) <= len(neighs) * (1 - x[s,wchr]))

    ## WCHB passengers
    wchb_seats = plane.wchb_seats
    for wchb in passengers.wchb:

        # WCHB are placed on the center of columns
        model.addConstr(sum([x[s,wchb] for s in wchb_seats]) == 1)
        
        for s in plane.wchb_seats:
            neighs = plane.wchb_neigh[s]
            model.addConstr(sum([x[s,p] for s in neighs for p in passengers.passengers]) <= len(neighs) * (1 - x[s,wchb]))

        for s in plane.wchb_seats:
            neighs = plane.wchb_neigh2_for_wchr[s]
            model.addConstr(sum([x[s,p] for s in neighs for p in passengers.wchr]) <= len(neighs) * (1 - x[s,wchb]))
    
    time_cost = 0
    
    for p in passengers.passengers:
        t_p = (1 - passengers.corresponding_times[p]/2) if passengers.corresponding_times[p]!= 0 else 0
        for s in plane.seats:
            time_cost += x[s,p]* t_p * (s//6+1)
    time_cost *= alpha 
    
    ### Objective function ###
    model.setObjective(sum([sum(Y[group].values()) for group in Y.keys()]) / 2 + time_cost + 1000 * sum(eps1.values()) + 100000 * sum(eps2.values()), gurobipy.GRB.MINIMIZE)
    model.params.TimeLimit = time_limit
    model.params.MIPGap = mip_gap
    # Set the callback function to be called every 1 second
    if callback:
        model.optimize(mycallback)

    else:
        model.optimize()
    

    # Print the solution
    #print("x =", {k: v.x for k, v in x.items()})
    #print("y =", {k: v.x for k, v in y.items()})
    print("Objective value =", model.objVal)

    passenger_on_seats = dict()
    for seat in plane.seats:
        for passenger in passengers.passengers:
            if x[(seat,passenger)].X > 1/2:
                passenger_on_seats[seat] = passenger


    return passenger_on_seats, (x_barycenter.getValue(),y_barycenter.getValue())

last_update_time = time.time()
def mycallback(model, where):
    global last_update_time
    if where == gurobipy.GRB.Callback.MIPSOL:
        #print('runtime: ',model.getAttr("RunTime"))
        last_update_time = time.time()

    # Stop the optimization if the objective value has not improved in the last minute
    if time.time() - last_update_time > 180:
        model.terminate()