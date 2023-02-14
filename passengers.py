import pandas as pd
import numpy as np
import datetime

class Passengers:

    "Explain Passengers class"

    def __init__(self, P, W, M, E, WCHR, WCHB, B, ECO, bounds, corresponding_times, woman_mass=60, man_mass=75, child_mass=40, wchr_mass=90, wchb_mass=90):
        self.passengers = P
        self.women = W
        self.men = M
        self.children = E
        self.wchr = WCHR
        self.wchb = WCHB
        self.business = B
        self.economy = ECO
        self.bounds = bounds
        self.mass = dict(woman=woman_mass, man=man_mass, child=child_mass, wchr=wchr_mass, wchb=wchb_mass)
        self.corresponding_times = corresponding_times

    def compute_groups_bounds(data):
        dict = {}
        compteur = 0
        
        for i in range(len(data)):
            group = []

            for w in range(int(data['Femmes'][i])):
                compteur += 1
                group.append(compteur)
            for m in range(int(data['Hommes'][i])):
                compteur += 1
                group.append(compteur)
            for e in range(int(data['Enfants'][i])):
                compteur += 1
                group.append(compteur)
            for wchr in range(int(data['WCHR'][i])):
                compteur += 1
                group.append(compteur)
            for wchv in range(int(data['WCHB'][i])):
                compteur += 1
                group.append(compteur)

            first_group_passenger = group[0]
            last_group_passenger = group[-1]

            dict[data["Numéro du groupe"][i]] = [first_group_passenger, last_group_passenger]
            
        return dict
    
    def get_group(self, passenger_id):
        for group_id, bounds in self.bounds.items():
            if passenger_id >= bounds[0] and passenger_id <= bounds[1]:
                return group_id

    def compute_passengers_sets(path):
        data = pd.read_csv(path, sep=';')
        data = data.fillna(value=0)
        P = []
        W = []
        M = []
        E = []
        WCHR = []
        WCHB = []
        B = []
        ECO =[]
        corresponding_times = dict()
        compteur = 0
        
        for i in range(len(data)):

            for w in range(int(data['Femmes'].iloc[i])):
                compteur += 1
                W.append(compteur)
                if data['Classe'][i] == "J":
                    B.append(compteur)
                else:
                    ECO.append(compteur)
                corresponding_times[compteur] = (datetime.datetime.strptime(data["TransitTime"].iloc[i], '%H:%M:%S') - datetime.datetime(1900, 1, 1)) // datetime.timedelta(minutes=1)

            for m in range(int(data['Hommes'][i])):
                compteur += 1
                M.append(compteur)
                if data['Classe'][i] == "J":
                    B.append(compteur)
                else:
                    ECO.append(compteur)
                corresponding_times[compteur] = (datetime.datetime.strptime(data["TransitTime"].iloc[i], '%H:%M:%S') - datetime.datetime(1900, 1, 1)) // datetime.timedelta(minutes=1)

            for e in range(int(data['Enfants'][i])):
                compteur += 1
                E.append(compteur)
                if data['Classe'][i] == "J":
                    B.append(compteur)
                else:
                    ECO.append(compteur)
                corresponding_times[compteur] = (datetime.datetime.strptime(data["TransitTime"].iloc[i], '%H:%M:%S') - datetime.datetime(1900, 1, 1)) // datetime.timedelta(minutes=1)

            for wchr in range(int(data['WCHR'][i])):
                compteur += 1
                WCHR.append(compteur)
                if data['Classe'][i] == "J":
                    B.append(compteur)
                else:
                    ECO.append(compteur)
                corresponding_times[compteur] = (datetime.datetime.strptime(data["TransitTime"].iloc[i], '%H:%M:%S') - datetime.datetime(1900, 1, 1)) // datetime.timedelta(minutes=1)

            for wchv in range(int(data['WCHB'][i])):
                compteur += 1
                WCHB.append(compteur)
                if data['Classe'][i] == "J":
                    B.append(compteur)
                else:
                    ECO.append(compteur)
                corresponding_times[compteur] = (datetime.datetime.strptime(data["TransitTime"].iloc[i], '%H:%M:%S') - datetime.datetime(1900, 1, 1)) // datetime.timedelta(minutes=1)

        t_max = max(corresponding_times.values())
        for p in corresponding_times.keys():
            corresponding_times[p] /= t_max

        P = [i for i in range(1, compteur+1)]
        bounds = Passengers.compute_groups_bounds(data)


        return Passengers(P, W, M, E, WCHR, WCHB, B, ECO, bounds, corresponding_times)
        
    
    def get_passenger_type(self, passenger_number):
        if passenger_number in self.men:
            return 'man'
        if passenger_number in self.women:
            return 'woman'
        if passenger_number in self.children:
            return 'child'
        if passenger_number in self.wchr:
            return 'wchr'
        if passenger_number in self.wchb:
            return 'wchb'

    def get_passenger_type(self, passenger_number):
        if passenger_number in self.men:
            return 'man'
        if passenger_number in self.women:
            return 'woman'
        if passenger_number in self.children:
            return 'child'
        if passenger_number in self.wchr:
            return 'wchr'
        if passenger_number in self.wchb:
            return 'wchb'
