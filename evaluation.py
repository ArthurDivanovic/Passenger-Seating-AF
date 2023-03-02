import planes
import passengers
import numpy as np

def best_metric(passengers, alpha=0):
    metric = 0

    for group in passengers.bounds.keys():
        first_element, last_element = passengers.bounds[group]
        
        group_size = last_element - first_element + 1

        new_group_size = group_size
        if first_element in passengers.business:
            if group_size % 4 == 0:
                new_group_size += group_size // 2
            elif group_size % 4 == 1:
                new_group_size += group_size // 2 + 5
            elif group_size % 4 == 2:
                new_group_size += (group_size // 2 - 1) + 4
            else:
                new_group_size += (group_size // 2 - 1) + 3
            
        
        plane = planes.Plane(nb_line=new_group_size//6+1)
        
        if group_size <= 3:
            a = plane.a_l3
        else:
            a = plane.a_u3

        x = dict()
        s = 1

        if first_element in passengers.business : 
            for p in range(first_element,last_element+1):
                x[p] = s
                if s%3 == 1:
                    s += 2
                else :
                    s += 1

        else :
            for p in range(first_element,last_element+1):
                x[p] = s
                s += 1
        

        group_metric = 0
        for p in range(first_element,last_element+1):
            s = x[p]
            for p_prime in range(first_element,last_element+1):
                s_prime = x[p_prime]
                group_metric += (abs(a[s][0] - a[s_prime][0]) + abs(a[s][1] - a[s_prime][1]))/2
        #print("group ", group, " ", passengers.bounds[group],  " : ", group_metric)
        metric += group_metric

    time_cost = 0
    corresponding_times_business = {key: value for key, value in passengers.corresponding_times.items() if value != 0 and key in passengers.business}
    corresponding_times_business = sorted(corresponding_times_business.items(), key=lambda t: t[1])

    corresponding_times_economy = {key: value for key, value in passengers.corresponding_times.items() if value != 0 and key not in passengers.business}
    corresponding_times_economy = sorted(corresponding_times_economy.items(), key=lambda t: t[1])

    s = 1
    for p, t in corresponding_times_business:
        time_cost += (1 - t/2) * (s//6+1)
        if s%3 == 1 :
            s += 2
        else :
            s += 1 

    if s%6 != 1 :
        line = planes.get_line(s)
        s = line*6 + 1
   
    for p, t in corresponding_times_economy:
        time_cost += (1 - t/2) * (s//6+1)
        s += 1
    metric += alpha * time_cost 
    return metric




def best_original_metric(passengers):
    metric = 0

    for group in passengers.bounds.keys():
        first_element, last_element = passengers.bounds[group]
        
        group_size = last_element - first_element + 1

        new_group_size = group_size
        if first_element in passengers.business:
            if group_size % 4 == 0:
                new_group_size += group_size // 2
            elif group_size % 4 == 1:
                new_group_size += group_size // 2 + 5
            elif group_size % 4 == 2:
                new_group_size += (group_size // 2 - 1) + 4
            else:
                new_group_size += (group_size // 2 - 1) + 3
            
        
        plane = planes.Plane(nb_line=new_group_size//6+1)
        
        if group_size <= 3:
            a = plane.original_a_l3
        else:
            a = plane.original_a_u3

        x = dict()
        s = 1

        if first_element in passengers.business : 
            for p in range(first_element,last_element+1):
                x[p] = s
                if s%3 == 1:
                    s += 2
                else :
                    s += 1

        else :
            for p in range(first_element,last_element+1):
                x[p] = s
                s += 1
        
        group_metric = 0
        for p in range(first_element,last_element+1):
            s = x[p]
            for p_prime in range(first_element,last_element+1):
                s_prime = x[p_prime]
                dist = (abs(a[s][0] - a[s_prime][0]) + abs(a[s][1] - a[s_prime][1]))
                group_metric += dist if dist <= 1 else 0

        #print("group ", group, " ", passengers.bounds[group],  " : ", group_metric)
        metric += group_metric

    time_cost = 0
    corresponding_times_business = {key: value for key, value in passengers.corresponding_times.items() if value != 0 and key in passengers.business}
    corresponding_times_business = sorted(corresponding_times_business.items(), key=lambda t: t[1])

    corresponding_times_economy = {key: value for key, value in passengers.corresponding_times.items() if value != 0 and key not in passengers.business}
    corresponding_times_economy = sorted(corresponding_times_economy.items(), key=lambda t: t[1])

    s = 1
    for p, t in corresponding_times_business:
        time_cost += (1 - t/2) * (s//6+1)
        if s%3 == 1 :
            s += 2
        else :
            s += 1 

    if s%6 != 1 :
        line = planes.get_line(s)
        s = line*6 + 1
   
    for p, t in corresponding_times_economy:
        time_cost += (1 - t/2) * (s//6+1)
        s += 1

    return metric, time_cost



def original_best_group_score(group_size):
    if group_size < 7 :
        return (group_size - 1)*2
    else :
        score_line = 10
        not_complete_line = group_size%6
        return group_size//6*score_line + original_best_group_score(not_complete_line) + not_complete_line*1



def evaluate_original_metric(plane, group_on_seats):
    if len(group_on_seats) <= 3 :
        a = plane.original_a_l3
    else:
        a = plane.original_a_u3

    original_metric = 0
    for s in group_on_seats.keys():
        for s_prime in group_on_seats.keys():
            dist = (abs(a[s][0] - a[s_prime][0]) + abs(a[s][1] - a[s_prime][1]))
            original_metric += dist if dist <= 1 else 0

    return original_metric