from evaluation import *
from copy import deepcopy

def final_heuristic_v1(plane, passengers, passengers_on_seats):
    moving_groups = dict()
    moving_seats = dict()
    for s in plane.seats :
        if s in passengers_on_seats :
            moving_seats[s] = False
        else :
            moving_seats[s] = True

    

    for group in passengers.bounds.keys():
        first_element, last_element = passengers.bounds[group]
        group_size = last_element - first_element + 1

        
        if first_element not in passengers.business:
            best_possible_group_score = original_best_group_score(group_size)

            group_on_seats = {key: value for key, value in passengers_on_seats.items() if value >= first_element and value <= last_element and key not in passengers.wchr and key not in passengers.wchb}

            #Groups of size 1
            if group_size == 1 and first_element not in passengers.wchr and first_element not in passengers.wchb:
                moving_groups[group] = group_on_seats
                for s in group_on_seats:
                    moving_seats[s] = True
            else :
                group_score = evaluate_original_metric(plane, group_on_seats)

                #Groups without best score
                if group_score != best_possible_group_score :
                    moving_groups[group] = group_on_seats
                    for s in group_on_seats:
                        moving_seats[s] = True
    
    x = {p:s for s,p in passengers_on_seats.items()}

    #We can't move wchr passengers or move a passenger in their neighborhood
    for p in passengers.wchr:
        moving_seats[x[p]] = False
        for s in plane.wchr_neigh[x[p]]:
            moving_seats[s] = False
    
    #We can't move wchb passengers or move a passenger in their neighborhood
    for p in passengers.wchb:
        moving_seats[x[p]] = False
        for s in plane.wchb_neigh[x[p]]:
            moving_seats[s] = False

    new_passengers_on_seats = deepcopy(passengers_on_seats)

    # for group in moving_groups:
    #     for p in moving_groups[group].values():
    #         s = x[p]
            


        
    return moving_groups, moving_seats