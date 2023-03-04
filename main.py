import numpy as np
import pandas as pd
import gurobipy

from passengers import *
from planes import *
from constraints import *
from soft_constraints import *

from final_heuristic import *


def compute_adapted_plane(passengers):
    n = required_plane_size(passengers)
    if n%6==0:
        n_rows = n // 6
    else:
        n_rows = n//6 + 1
    exit_lines = [n_rows // 2]
    plane = Plane(n_rows, exit_lines=exit_lines)
    return plane

def required_plane_size(passengers):

    size = 0
    nb_passengers = len(passengers.passengers)
    size += nb_passengers

    # Add the contribution in the number of seats needed from WCHR passengers
    wchr = passengers.wchr
    size += len(wchr) * 3     

    # Add the contribution in the number of seats needed from WCHB passengers
    wchb = passengers.wchb
    size += len(wchb) * 11      

    # Add the contribution in the number of seats needed from business passengers
    business = passengers.business
    bus = len(business)
    if bus % 4 == 0:
        size += bus // 2
    elif bus % 4 == 1:
        size += bus // 2 + 5
    elif bus % 4 == 2:
        size += (bus // 2 - 1) + 4
    else:
        size += (bus // 2 - 1) + 3

    return size 

def computer_passenger_seating(path, plane_size=152, time_limit=300, alpha=0.1, mip_gap=0.7, callback=True, name="results", path_for_results="", save=True, plot=True):

    ## Passengers info collecting
    passengers = Passengers.compute_passengers_sets(path)
    # print('nb_passengers :', len(passengers.passengers))
    # print('required :', required_plane_size(passengers))
    plane = compute_adapted_plane(passengers)
    # print('actual :', len(plane.seats))
    
    ## Plane simulation

    # Check if the passenger seating problem is feasible
    # required_size = required_plane_size(passengers)
    # try:
    #     assert(required_size <= plane_size)
    # except:
    #     raise AttributeError(f'The passengers dataset is invalid, there are too many people to fit in an A320')

    # # Buil plane object
    # if plane_size % 6==0:
    #     n_rows = plane_size// 6
    # else:
    #     n_rows = plane_size//6 + 1
    # exit_lines = [n_rows // 2]
    # plane = Plane(n_rows, exit_lines=exit_lines)

    ## Solve problem

    # Solving with gurobi
    x, barycenter = gurobi_solving(passengers,plane, time_limit=time_limit, alpha=alpha, mip_gap=mip_gap, callback=callback)

    # Ploting results 
    if plot:
       plot_results_from_solver(passengers, plane, x, barycenter, title=name+" after gurobi solving")

    #Heuristics   
    x, barycenter = final_heuristic_v1(plane, passengers, x, barycenter, alpha)

    # Ploting results 
    if plot:
       plot_results_from_solver(passengers, plane, x, barycenter,  title=name+" after heuristics solving")

    if save: 
        # Save results
        seating_df = pd.DataFrame(x.items(), columns=['seat_number','passenger_id'])
        seating_df.sort_values(by = 'passenger_id', inplace=True)
        seating_df.set_index('passenger_id', inplace=True)
        seating_df["group"] = [passengers.get_group(idx) for idx in seating_df.index]
        seating_df["is_child"] = [1 if passengers.get_passenger_type(idx) == "child" else 0 for idx in seating_df.index]
        seating_df["is_man"] = [1 if passengers.get_passenger_type(idx) == "man" else 0 for idx in seating_df.index]
        seating_df["is_woman"] = [1 if passengers.get_passenger_type(idx) == "woman" else 0 for idx in seating_df.index]
        seating_df["is_wchr"] = [1 if passengers.get_passenger_type(idx) == "wchr" else 0 for idx in seating_df.index]
        seating_df["is_wchb"] = [1 if passengers.get_passenger_type(idx) == "wchb" else 0 for idx in seating_df.index]
        seating_df.loc[0] = [plane.nb_seat//6, plane.exit_lines, barycenter, 0, 0, 0, 0]
        seating_df.sort_index(inplace=True)
        seating_df.to_csv(f"{path_for_results}{name}.csv")

    return passengers, plane, x, barycenter


def computer_soft_passenger_seating(path, plane_size=152, time_limit=300, alpha=0.1, mip_gap=0.7, callback=True, name="", path_for_results="", save=True, plot=True):

    ## Passengers info collecting
    passengers = Passengers.compute_passengers_sets(path)
    print('required :', required_plane_size(passengers))
    plane = compute_adapted_plane(passengers)
    print('actual :', len(plane.seats))
    
    ## Plane simulation

    # Check if the passenger seating problem is feasible
    # required_size = required_plane_size(passengers)
    # try:
    #     assert(required_size <= plane_size)
    # except:
    #     raise AttributeError(f'The passengers dataset is invalid, there are too many people to fit in an A320')

    # # Buil plane object
    # if plane_size % 6==0:
    #     n_rows = plane_size// 6
    # else:
    #     n_rows = plane_size//6 + 1
    # exit_lines = [n_rows // 2]
    # plane = Plane(n_rows, exit_lines=exit_lines)

    ## Solve problem

    # Solving with gurobi
    x, barycenter = soft_gurobi_solving(passengers,plane, time_limit=time_limit, alpha=alpha, mip_gap=mip_gap, callback=callback)

    # Ploting results 
    if plot:
       plot_results_from_solver(passengers, plane, x, barycenter, title=name+" after gurobi solving")

    #Heuristics   
    x, barycenter = final_heuristic_soft(plane, passengers, x, barycenter, alpha)

    if plot:
       plot_results_from_solver(passengers, plane, x, barycenter, title=name+" after heuristics solving")

    if save: 
        # Save results
        seating_df = pd.DataFrame(x.items(), columns=['seat_number','passenger_id'])
        seating_df.sort_values(by = 'passenger_id', inplace=True)
        seating_df.set_index('passenger_id', inplace=True)
        seating_df["group"] = [passengers.get_group(idx) for idx in seating_df.index]
        seating_df["is_child"] = [1 if passengers.get_passenger_type(idx) == "child" else 0 for idx in seating_df.index]
        seating_df["is_man"] = [1 if passengers.get_passenger_type(idx) == "man" else 0 for idx in seating_df.index]
        seating_df["is_woman"] = [1 if passengers.get_passenger_type(idx) == "woman" else 0 for idx in seating_df.index]
        seating_df["is_wchr"] = [1 if passengers.get_passenger_type(idx) == "wchr" else 0 for idx in seating_df.index]
        seating_df["is_wchb"] = [1 if passengers.get_passenger_type(idx) == "wchb" else 0 for idx in seating_df.index]
        seating_df.loc[0] = [plane.nb_seat//6, plane.exit_lines, barycenter, 0, 0, 0, 0]
        seating_df.sort_index(inplace=True)
        seating_df.to_csv(f"{path_for_results}{name}.csv")
    
    

    return passengers, plane, x, barycenter




