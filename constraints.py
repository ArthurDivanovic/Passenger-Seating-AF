import pandas as pd
import numpy as np
from pulp import *
from planes import *
from passengers import *
import matplotlib.pyplot as plt


def create_constraints(passengers, plane):

    # Problem
    prob = LpProblem("Passenger Seating Problem", LpMinimize)

    # Variables
    nb_p = len(passengers.passengers)
    nb_s = plane.nb_seat
    x = LpVariable.dicts("x[i,j]", (range(1, nb_s+1), range(1, nb_p+1)), lowBound=0, upBound=1, cat="Binary")
    Y = dict()
    for group in passengers.bounds.keys():
        first_element = passengers.bounds[group][0]
        last_element = passengers.bounds[group][1]
        Y[group] = LpVariable.dict("y"+str(group)+"[i,j]", (range(first_element, last_element+1), range(first_element, last_element+1)), 0, None)

    # Objective function

    obj = 0
    for group in Y.keys():
        y = Y[group]
        first_element = passengers.bounds[group][0]
        last_element = passengers.bounds[group][1]
        obj += lpSum(y[i,j] for i in range(first_element, last_element+1) for j in range(first_element, last_element+1)) / 2

    prob += obj
    print('Objective :',prob.objective)

    ### CONSTRAINTS ###
    #for p in passengers.passengers:
    #    for s in plane.seats:
    #        prob += x[s][p] >= 0
    ## Children passengers
    emergency_seats = plane.emergency_seats
    for c in passengers.children:

        # No children next to the emergency exits
        prob += lpSum([x[s][c] for s in emergency_seats]) == 0

        # Children should have an adult next to them
        adults = passengers.men + passengers.women
        for s in plane.seats:
            neighs = plane.child_neigh[s]
            prob += lpSum([x[s][p] for s in neighs for p in adults]) >= x[s][c]

    ## WCHR passengers
    alley_seats = plane.alley_seats
    for wchr in passengers.wchr:

        # WCHR are placed on the alleys
        prob += lpSum([x[s][wchr] for s in alley_seats]) == 1

        # WCHR freeze seats around them
        prob += lpSum([x[s][wchr] for s in range(1,7)]) == 0
        for s in plane.wchr_seats:
            neighs = plane.wchr_neigh[s]
            prob += lpSum([x[s][wchr] for s in neighs]) <= len(neighs) * (1 - x[s][wchr])

    ## WCHB passengers
    for wchb in passengers.wchb:
        
        prob += lpSum([x[s][wchb] for s in range(1,19)]) == 0
        for s in plane.wchb_seats:
            neighs = plane.wchb_neigh[s]
            prob += lpSum([x[s][wchb] for s in neighs]) <= len(neighs) * (1 - x[s][wchb])

    ## Business passengers
    for b in passengers.business:

        # Business passengers are placed on the business seats
        business_seats = plane.business_seats
        prob += lpSum([x[s][b] for s in business_seats]) == 1

        # Business passengers have no direct neighbors
        for s in business_seats:
            neighs = plane.business_neigh[s]
            prob += lpSum([x[s][p] for s in neighs for p in passengers.passengers]) <= len(neighs) * (1 - x[s,b])


    #Barycenter within the center zone
    #xmin = plane.seat_position[plane.center_zone[0]][0]
    #xmax = plane.seat_position[plane.center_zone[1]][0]
    #ymin = plane.seat_position[plane.center_zone[0]][1]
    #ymax = plane.seat_position[plane.center_zone[2]][1]
    #x_barycenter = 1/nb_p * lpSum([x[s][p]*plane.seat_position[s][0]*passengers.mass[passengers.get_passenger_type(p)] for s in neighs for p in passengers.passengers])
    #y_barycenter = 1/nb_p * lpSum([x[s][p]*plane.seat_position[s][1]*passengers.mass[passengers.get_passenger_type(p)] for s in neighs for p in passengers.passengers])
    #prob +=  x_barycenter <= xmax
    #prob +=  x_barycenter >= xmin
    #prob +=  y_barycenter <= ymax
    #prob +=  y_barycenter >= ymin
   
            
    ## Only one seat per passenger 
    for p in passengers.passengers:
        prob +=  lpSum([x[s][p] for s in plane.seats]) == 1
    
    ## Only one passenger per seat 
    for s in plane.seats:
        prob += lpSum([x[s][p] for p in passengers.passengers]) <= 1

    ## Constraints on y
    a_u3 = plane.a_u3
    a_l3 = plane.a_l3
    seats = plane.seats
    for group in Y.keys():
        group_passengers = passengers.bounds[group]
        y = Y[group]
        if len(y) <= 3:
            a = a_l3
        else:
            a = a_u3
        for p in range(group_passengers[0],group_passengers[1]+1):
            for p_prime in range(group_passengers[0],group_passengers[1]+1):

                prob += y[p,p_prime] >= lpSum([(x[s][p]- x[s][p_prime])*(a[s][0] + a[s][1]) for s in seats]) 
                prob += y[p,p_prime] >= lpSum([(x[s][p]- x[s][p_prime])*(a[s][0] - a[s][1]) for s in seats])
                prob += y[p,p_prime] >= lpSum([(x[s][p]- x[s][p_prime])*(-a[s][0] + a[s][1]) for s in seats])
                prob += y[p,p_prime] >= lpSum([(x[s][p]- x[s][p_prime])*(-a[s][0] - a[s][1]) for s in seats])
        

    ### SOLVE PROBLEM ###
    status = prob.solve(PULP_CBC_CMD(msg=1))

    ### DISPLAY SOLUTION ###
    print(f'Optimal solution: {value(prob.objective)}')
    for s in plane.seats:
        for p in passengers.passengers:
            print(f'x[{s},{p}] = {x[s][p].varValue}')
    for group in Y.keys():
        print('group: ',group)
        group_passengers = passengers.bounds[group]
        print('group passengers :', group_passengers)
        y = Y[group]
        print('y :', y)
        for p in range(group_passengers[0],group_passengers[1]+1):
            for p_prime in range(group_passengers[0],group_passengers[1]+1):
                print(f'y[{p},{p_prime}] = {y[p,p_prime].varValue}')

def gurobi_solving(passengers, plane):

    # Model
    model = gurobipy.Model("Passenger Seating Problem")

    # Variables
    nb_p = len(passengers.passengers)
    nb_s = plane.nb_seat
    x = {(i, j): model.addVar(vtype=gurobipy.GRB.BINARY, name="x[i,j]") for i in range(1, nb_s+1) for j in range(1, nb_p+1)}
    Y = dict()
    for group in passengers.bounds.keys():
        first_element = passengers.bounds[group][0]
        last_element = passengers.bounds[group][1]
        Y[group] = {(i, j): model.addVar(name="y"+str(group)+"[i,j]") for i in range(first_element, last_element+1) for j in range(first_element, last_element+1)}

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

    ### Objective function ###
    model.setObjective(sum([sum(Y[group].values()) for group in Y.keys()]) / 2, gurobipy.GRB.MINIMIZE)
    model.params.TimeLimit = 300
    model.optimize()

    # Print the solution
    print("x =", {k: v.x for k, v in x.items()})
    print("y =", {k: v.x for k, v in y.items()})
    print("Objective value =", model.objVal)

    passenger_on_seats = dict()
    print(type(x))
    for seat in plane.seats:
        for passenger in passengers.passengers:
            if x[(seat,passenger)].X > 1/2:
                passenger_on_seats[seat] = passenger


    return passenger_on_seats

def plot_results(passengers, plane, passenger_on_seats):
    fig = plt.figure(figsize=(15,15))
    X = []
    Y = []
    for x,y in plane.seat_position.values():
        X.append(x)
        Y.append(y)
    plt.scatter(X,Y)

    X1, Y1 = [], []
    for s in plane.center_zone :
        x,y = plane.seat_position[s]
        X1.append(x)
        Y1.append(y)
    plt.scatter (X1,Y1, c='red')

    for s,p in passenger_on_seats.items():
        group_id = passengers.get_group(p)
        x,y = plane.seat_position[s]
        c = "black"
        if p in passengers.wchr :
            c="orange"
        if p in passengers.wchb:
            c="green"
        plt.text(x-0.2,y+0.3,s=group_id, fontdict=dict(color=c,size=20),)
