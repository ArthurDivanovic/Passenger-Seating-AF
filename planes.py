def get_column(seat_nb):
        return seat_nb%6
    
def get_line(seat_nb):
        return (seat_nb-1)//6+1

#METRIC FEATURES

#GROUP UNDER 3 PASSENGERS
ALLEY_SIZE_L3 = 2
LINE_SIZE_L3 = 20
COLUMN_SIZE_L3 = 1

#GROUP OVER 3 PASSENGERS
ALLEY_SIZE_U3 = 0
LINE_SIZE_U3 = 5
COLUMN_SIZE_U3 = 1



class Plane:

    '[Explain Plane class]' 

    def add_seats(self, new_seats):
        new_seats2 = []
        for s in new_seats :
            if s  <= self.nb_seat and s >= 0 :
                new_seats2.append(s)
        return new_seats2
    

    
    def __init__(self, nb_line=100, exit_lines=[], business_line_bound=0):
        
        self.nb_seat= nb_line * 6
        self.seats = [k for k in range(1, self.nb_seat+1)]

        self.exit_lines = exit_lines
        self.emergency_seats = [6 * (line-1) + 1 for line in exit_lines] + [6 * line for line in exit_lines]
        
        self.alley_seats = []
        for s in self.seats :
            if s%6 == 3 or s%6 == 4:
                self.alley_seats.append(s)
        
        self.child_neigh = dict()
        for s in self.seats:
            if s%6 == 3 or s%6 == 0:
                self.child_neigh[s] = self.add_seats([s-1])
            if s%6 == 4 or s%6 == 1:
                self.child_neigh[s] = self.add_seats([s+1])
            else :
                self.child_neigh[s] = self.add_seats([s-1, s+1])

        self.wchr_seats = self.alley_seats[2:]
        self.wchr_neigh = dict()
        for s in self.wchr_seats:
            if s%6 == 3:
                self.wchr_neigh[s] = self.add_seats([s-6, s-6-1, s-1])
            if s%6 == 4:
                self.wchr_neigh[s] = self.add_seats([s-6, s-6+1, s+1])

        self.wchb_seats = []
        self.wchb_neigh = dict()

        for s in self.seats[18:]:
            if s%6 == 2 or s%6 == 5 and s//6 > 2:
                self.wchb_seats.append(s)
                self.wchb_neigh[s] = self.add_seats([s-1, s+1, s-6-1, s-6, s-6+1, s-12-1,s-12, s-12+1, s-18-1, s-18, s-18+1])

        self.wchb_neigh2_for_wchr = dict()
        for s in self.wchb_seats:
            if s%6 == 2:
                self.wchb_neigh2_for_wchr[s] = self.add_seats([s+6, s+6+1, s+6-1, s+2, s+6+2, s-6+2, s-12+2, s-18+2])
            if s%6 == 5:
                self.wchb_neigh2_for_wchr[s] = self.add_seats([s+6, s+6+1, s+6-1, s-2, s+6-2, s-6-2, s-12-2, s-18-2])

        self.business_seats = []    

        self.business_neigh = dict()
        for s in self.seats:
            if s%6 == 3 or s%6 == 0:
                self.business_neigh[s] = self.add_seats([s-1])
            elif s%6 == 4 or s%6 == 1:
                self.business_neigh[s] = self.add_seats([s+1])
            else :
                self.business_neigh[s] = self.add_seats([s-1, s+1])

        
        
        #Seat position for barycenter
        alley_size = 1
        line_size = 3
        column_size = 1
        self.seat_position = dict()
        for s in self.seats:
            if s%6 <= 3 and s%6 >= 1:
                self.seat_position[s] = [s%6*column_size, (s//6+1)*line_size]
            else:
                if s%6 == 0:
                    self.seat_position[s] = [alley_size + 6*column_size, s//6*line_size]
                else :
                    self.seat_position[s] = [alley_size + s%6*column_size, (s//6+1)*line_size]
        
        # 4 seats defining the square (front seat first)
        if nb_line%2 == 1:
            mid_line = nb_line//2+1
            self.center_zone = self.add_seats([mid_line*6 - 3 - 12, mid_line*6 - 2 - 12, mid_line*6 - 3 + 12, mid_line*6 - 2 + 12])
        else :
            mid_line = nb_line//2
            self.center_zone = self.add_seats([mid_line*6 - 3 - 6, mid_line*6 - 2 - 6, mid_line*6 - 3 + 12, mid_line*6 - 2 + 12])
        

        #Position for group of less (or equal) than 3 people
        alley_size_l3 = ALLEY_SIZE_L3
        line_size_l3 = LINE_SIZE_L3
        column_size_l3 = COLUMN_SIZE_L3

        self.a_l3 = dict()
        for s in self.seats:
            if s%6 <= 3 and s%6 >= 1:
                self.a_l3[s] = [s%6*column_size_l3, (s//6+1)*line_size_l3]
            else:
                if s%6 == 0:
                    self.a_l3[s] = [alley_size_l3 + 6*column_size_l3, s//6*line_size_l3]
                else :
                    self.a_l3[s] = [alley_size_l3 + s%6*column_size_l3, (s//6+1)*line_size_l3]


        #Position for group of more than 3 people
        alley_size_u3 = ALLEY_SIZE_U3
        line_size_u3 = LINE_SIZE_U3
        column_size_u3 = COLUMN_SIZE_U3

        self.a_u3 = dict()
        for s in self.seats:
            if s%6 <= 3 and s%6 >= 1:
                self.a_u3[s] = [s%6*column_size_u3, (s//6+1)*line_size_u3]
            else:
                if s%6 == 0:
                    self.a_u3[s] = [alley_size_u3 + 6*column_size_u3, s//6*line_size_u3]
                else :
                    self.a_u3[s] = [alley_size_u3 + s%6*column_size_u3, (s//6+1)*line_size_u3]




        
        #Original metric for group of less (or equal) than 3 people
        original_alley_size_l3 = 1
        original_line_size_l3 = 2
        original_column_size_l3 = 1

        self.original_a_l3 = dict()
        for s in self.seats:
            if s%6 <= 3 and s%6 >= 1:
                self.original_a_l3[s] = [s%6*original_column_size_l3, (s//6+1)*original_line_size_l3]
            else:
                if s%6 == 0:
                    self.original_a_l3[s] = [original_alley_size_l3 + 6*original_column_size_l3, s//6*original_line_size_l3]
                else :
                    self.original_a_l3[s] = [original_alley_size_l3 + s%6*original_column_size_l3, (s//6+1)*original_line_size_l3]


        #Original metric for group of more than 3 people
        original_alley_size_u3 = 0
        original_line_size_u3 = 0.5
        original_column_size_u3 = 1

        self.original_a_u3 = dict()
        for s in self.seats:
            if s%6 <= 3 and s%6 >= 1:
                self.original_a_u3[s] = [s%6*original_column_size_u3, (s//6+1)*original_line_size_u3]
            else:
                if s%6 == 0:
                    self.original_a_u3[s] = [original_alley_size_u3 + 6*original_column_size_u3, s//6*original_line_size_u3]
                else :
                    self.original_a_u3[s] = [original_alley_size_u3 + s%6*original_column_size_u3, (s//6+1)*original_line_size_u3]


