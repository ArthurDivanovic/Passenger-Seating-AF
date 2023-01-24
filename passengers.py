import pandas as pd
import numpy as np

class Passengers:

    "Explain Passengers class"

    def __init__(self, P, W, M, E, WCHR, WCHB, B, bounds):
        self.passengers = P
        self.women = W
        self.men = M
        self.children = E
        self.wchr = WCHR
        self.wchb = WCHB
        self.businness = B
        self.bounds = bounds


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
        compteur = 0
        
        for i in range(len(data)):

            for w in range(int(data['Femmes'].iloc[i])):
                compteur += 1
                W.append(compteur)
                if data['Classe'][i] == "J":
                    B.append(compteur)
            for m in range(int(data['Hommes'][i])):
                compteur += 1
                M.append(compteur)
                if data['Classe'][i] == "J":
                    B.append(compteur)
            for e in range(int(data['Enfants'][i])):
                compteur += 1
                E.append(compteur)
                if data['Classe'][i] == "J":
                    B.append(compteur)
            for wchr in range(int(data['WCHR'][i])):
                compteur += 1
                WCHR.append(compteur)
                if data['Classe'][i] == "J":
                    B.append(compteur)
            for wchv in range(int(data['WCHB'][i])):
                compteur += 1
                WCHB.append(compteur)
                if data['Classe'][i] == "J":
                    B.append(compteur)

        P = [i for i in range(1, compteur+1)]
        bounds = Passengers.compute_groups_bounds(data)

        return Passengers(P, W, M, E, WCHR, WCHB, B, bounds)

