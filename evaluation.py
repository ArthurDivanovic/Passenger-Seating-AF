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



def best_original_metric(passengers, alpha):
    metric = 0

    for group in passengers.bounds.keys():
        first_element, last_element = passengers.bounds[group]
        
        if first_element not in passengers.business:
            
            group_size = last_element - first_element + 1
            plane = planes.Plane(nb_line=group_size//6+1)
        
            if group_size <= 3:
                a = plane.original_a_l3
            else:
                a = plane.original_a_u3

            x = dict()
            s = 1

            for p in range(first_element,last_element+1):
                x[p] = s
                s += 1
            
            group_metric = 0
            for p in range(first_element,last_element+1):
                s = x[p]
                for p_prime in range(first_element,last_element+1):
                    s_prime = x[p_prime]

                    #s and s_prime have max one line of difference
                    if abs((s_prime-1)//6 - (s-1)//6) <= 1:
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

    return metric - alpha*time_cost



def original_best_group_score(group_size):
    if group_size < 7 :
        return (group_size - 1)*2
    else :
        score_line = 10
        not_complete_line = group_size%6
        return group_size//6*score_line + original_best_group_score(not_complete_line) + not_complete_line*1



def evaluate_group_original_metric(plane, group_on_seats):
    if len(group_on_seats) <= 3 :
        a = plane.original_a_l3
    else:
        a = plane.original_a_u3

    original_metric = 0
    for s in group_on_seats.keys():
        for s_prime in group_on_seats.keys():
            #s and s_prime have max one line of difference
            if abs((s_prime-1)//6 - (s-1)//6) <= 1:
                dist = (abs(a[s][0] - a[s_prime][0]) + abs(a[s][1] - a[s_prime][1]))
                original_metric += dist if dist <= 1 else 0

    return original_metric


def evaluate_original_metric(plane, passengers, passengers_on_seats, alpha):
    original_metric = 0
    
    for group in passengers.bounds.keys():
        first_element, last_element = passengers.bounds[group]

        if first_element not in passengers.business:
            group_on_seats = {key: value for key, value in passengers_on_seats.items() if value >= first_element and value <= last_element}
            original_metric += evaluate_group_original_metric(plane, group_on_seats)

        time_cost = 0
    
    for s,p in passengers_on_seats.items() :
        t_p = (1 - passengers.corresponding_times[p]/2) if passengers.corresponding_times[p]!= 0 else 0
        time_cost += t_p * (s//6+1)
    time_cost *= alpha 

    original_metric -= time_cost
    return original_metric


def check_constraints(plane, passengers, passengers_on_seats):
    

    # Barycenter 
    x_barycenter = 0
    y_barycenter = 0
    total_mass = sum([passengers.mass[passengers.get_passenger_type(p)] for p in passengers.passengers])

    for s,p in passengers_on_seats.items():
        m_p = passengers.mass[passengers.get_passenger_type(p)]
        x_barycenter += plane.seat_position[s][0] * m_p
        y_barycenter += plane.seat_position[s][1] * m_p

    x_barycenter /= total_mass
    y_barycenter /= total_mass

    xmin = plane.seat_position[plane.center_zone[0]][0]
    xmax = plane.seat_position[plane.center_zone[1]][0]
    ymin = plane.seat_position[plane.center_zone[0]][1]
    ymax = plane.seat_position[plane.center_zone[2]][1]

    if x_barycenter < xmin or x_barycenter > xmax or y_barycenter < ymin or y_barycenter > ymax:
        return None
    
    # Children not on emergency seats 
    for s in plane.emergency_seats :
        if s in passengers_on_seats and passengers_on_seats[s] in passengers.children :
            return None
    
    x = {p:s for s,p in passengers_on_seats.items()}
    
    # Children not alone
    adults = passengers.men + passengers.women
    for p in passengers.children:
        s = x[p]
        neighs = plane.child_neigh[s]
        check = False
        for s_prime in neighs :
            if s_prime in passengers_on_seats and passengers_on_seats[s_prime] in adults:
                check = True
                break
        if not check:
            return None
    
    return [x_barycenter, y_barycenter]


def check_soft_constraints(plane, passengers, passengers_on_seats):
    

    # Barycenter 
    x_barycenter = 0
    y_barycenter = 0
    total_mass = sum([passengers.mass[passengers.get_passenger_type(p)] for p in passengers.passengers])

    for s,p in passengers_on_seats.items():
        m_p = passengers.mass[passengers.get_passenger_type(p)]
        x_barycenter += plane.seat_position[s][0] * m_p
        y_barycenter += plane.seat_position[s][1] * m_p

    x_barycenter /= total_mass
    y_barycenter /= total_mass

    xmin = plane.seat_position[plane.center_zone[0]][0]
    xmax = plane.seat_position[plane.center_zone[1]][0]
    ymin = plane.seat_position[plane.center_zone[0]][1]
    ymax = plane.seat_position[plane.center_zone[2]][1]

    if x_barycenter < xmin or x_barycenter > xmax or y_barycenter < ymin or y_barycenter > ymax:
        return None
    
    # Children not on emergency seats 
    for s in plane.emergency_seats :
        if s in passengers_on_seats and passengers_on_seats[s] in passengers.children :
            return None
    
    return [x_barycenter, y_barycenter]