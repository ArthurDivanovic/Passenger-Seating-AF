from evaluation import *
from copy import deepcopy
from constraints import *

def final_heuristic_v1(plane, passengers, passengers_on_seats, barycenter, alpha):
    moving_groups = dict()
    moving_seats = dict()


    business_size = len(passengers.business)
    if business_size % 4 == 0:
        business_size += business_size // 2
    elif business_size % 4 == 1:
        business_size += business_size // 2 + 5
    elif business_size % 4 == 2:
        business_size += (business_size // 2 - 1) + 4
    else:
        business_size += (business_size // 2 - 1) + 3

    
    for s in plane.seats[business_size:]:
        if s in passengers_on_seats:
            moving_seats[s] = False
        else :
            moving_seats[s] = True
    
    
    x = {p:s for s,p in passengers_on_seats.items()}

    GROUPS_ON_SEAT = dict()

    for group in passengers.bounds.keys():
        first_element, last_element = passengers.bounds[group]
        group_size = last_element - first_element + 1

        
        if first_element not in passengers.business:
            best_possible_group_score = original_best_group_score(group_size)

            group_on_seats = {key: value for key, value in passengers_on_seats.items() if value >= first_element and value <= last_element}
            GROUPS_ON_SEAT[group] = group_on_seats

            group_on_seats_without_wch = {key: value for key, value in passengers_on_seats.items() if value >= first_element and value <= last_element and value not in passengers.wchr and value not in passengers.wchb}

            #Groups of size 1 can be moved 
            if group_size == 1:
                for s in group_on_seats_without_wch:
                    moving_seats[s] = True

            else :
                group_score = evaluate_group_original_metric(plane, group_on_seats)

                #Groups without best score
                if group_score != best_possible_group_score :
                    moving_groups[group] = group_on_seats_without_wch
                    for s in group_on_seats_without_wch:
                        moving_seats[s] = True
    
    

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

    
    moving_seats = [s for s in moving_seats if moving_seats[s]]
    
    actual_score = evaluate_original_metric(plane, passengers, passengers_on_seats, alpha)

    print("moving seats : ", moving_seats)
    print("actual score : ", actual_score)
    print("moving groups : ",moving_groups)

    for group in moving_groups:
        first_element, last_element = passengers.bounds[group]
        group_size = last_element - first_element + 1

        for p in moving_groups[group].values():
            for s_prime in moving_seats:
                
                s = x[p]

                new_passengers_on_seats = deepcopy(passengers_on_seats)
                
                new_passengers_on_seats[s_prime] = p

                #If a passenger is on s_prime
                if s_prime in passengers_on_seats:
                    p_prime = passengers_on_seats[s_prime]
                    new_passengers_on_seats[s] = p_prime

                else :
                    p_prime = None
                    del new_passengers_on_seats[s]

                new_score = evaluate_original_metric(plane, passengers, new_passengers_on_seats, alpha)
                # print("group ", group , " | p,s : ", p,s, " | p_prime, s_prime : ", p_prime, s_prime, " | new_score : ", new_score)
                if new_score > actual_score:
                    print("group ", group , " | p,s : ", p,s, " | p_prime, s_prime : ", p_prime, s_prime, " | new_score : ", new_score)

                    new_barycenter = check_soft_constraints(plane, passengers, new_passengers_on_seats)
                    if  new_barycenter != None :
                        barycenter = new_barycenter
                        passengers_on_seats = new_passengers_on_seats
                        actual_score = new_score
                    
                        x[p] = s_prime
                        if p_prime != None :
                            x[p_prime] = s


    return passengers_on_seats, barycenter






def final_heuristic_soft(plane, passengers, passengers_on_seats, barycenter, alpha):
    moving_groups = dict()
    moving_seats = dict()


    business_size = len(passengers.business)
    if business_size % 4 == 0:
        business_size += business_size // 2
    elif business_size % 4 == 1:
        business_size += business_size // 2 + 5
    elif business_size % 4 == 2:
        business_size += (business_size // 2 - 1) + 4
    else:
        business_size += (business_size // 2 - 1) + 3

    
    for s in plane.seats[business_size:]:
        if s in passengers_on_seats:
            moving_seats[s] = False
        else :
            moving_seats[s] = True
    
    
    x = {p:s for s,p in passengers_on_seats.items()}

    GROUPS_ON_SEAT = dict()

    for group in passengers.bounds.keys():
        first_element, last_element = passengers.bounds[group]
        group_size = last_element - first_element + 1

        
        if first_element not in passengers.business:
            best_possible_group_score = original_best_group_score(group_size)

            group_on_seats = {key: value for key, value in passengers_on_seats.items() if value >= first_element and value <= last_element}
            GROUPS_ON_SEAT[group] = group_on_seats

            group_on_seats_without_wch = {key: value for key, value in passengers_on_seats.items() if value >= first_element and value <= last_element and value not in passengers.wchr and value not in passengers.wchb}

            #Groups of size 1 can be moved 
            if group_size == 1:
                for s in group_on_seats_without_wch:
                    moving_seats[s] = True

            else :
                group_score = evaluate_group_original_metric(plane, group_on_seats)

                #Groups without best score
                if group_score != best_possible_group_score :
                    moving_groups[group] = group_on_seats_without_wch
                    for s in group_on_seats_without_wch:
                        moving_seats[s] = True
    
    

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

    
    moving_seats = [s for s in moving_seats if moving_seats[s]]
    
    actual_score = evaluate_original_metric(plane, passengers, passengers_on_seats, alpha)

    print("moving seats : ", moving_seats)
    print("actual score : ", actual_score)
    print("moving groups : ",moving_groups)

    for group in moving_groups:
        first_element, last_element = passengers.bounds[group]
        group_size = last_element - first_element + 1

        for p in moving_groups[group].values():
            for s_prime in moving_seats:
                
                s = x[p]

                new_passengers_on_seats = deepcopy(passengers_on_seats)
                
                new_passengers_on_seats[s_prime] = p

                #If a passenger is on s_prime
                if s_prime in passengers_on_seats:
                    p_prime = passengers_on_seats[s_prime]
                    new_passengers_on_seats[s] = p_prime

                else :
                    p_prime = None
                    del new_passengers_on_seats[s]

                new_score = evaluate_original_metric(plane, passengers, new_passengers_on_seats, alpha)
                # print("group ", group , " | p,s : ", p,s, " | p_prime, s_prime : ", p_prime, s_prime, " | new_score : ", new_score)
                if new_score > actual_score:

                    new_barycenter = check_soft_constraints(plane, passengers, new_passengers_on_seats)
                    if  new_barycenter != None :
                        barycenter = new_barycenter
                        print("group ", group , " | p,s : ", p,s, " | p_prime, s_prime : ", p_prime, s_prime, " | new_score : ", new_score)
                        passengers_on_seats = new_passengers_on_seats
                        actual_score = new_score
                    
                        x[p] = s_prime
                        if p_prime != None :
                            x[p_prime] = s


    return passengers_on_seats, barycenter