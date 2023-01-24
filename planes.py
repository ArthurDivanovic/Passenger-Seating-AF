class Plane:

    '[Explain Plane class]' 
    
    def get_column(self, seat_nb):
        return seat_nb%6
    
    def get_line(self, seat_nb):
        return seat_nb//6

    def add_seats(self, new_seats):
        new_seats2 = []
        for s in new_seats :
            if s  <= self.nb_seat and s >= 0 :
                new_seats2.append(s)
        return new_seats2
    
    def __init__(self, nb_line=100, exit_lines=[], business_line_bound=0):
        
        self.nb_seat= nb_line * 6
        self.seats = [k for k in range(1, self.nb_seat+1)]
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

        self.wchr_seats = self.alley_seats[1:]
        self.wchr_neigh = dict()
        for s in self.wchr_seats:
            if s%6 == 3:
                self.wchr_neigh[s] = self.add_seats([s-6, s-6+1, s+1])
            if s%6 == 4:
                self.wchr_neigh[s] = self.add_seats([s-6, s-6-1, s-1])

        self.wchb_seats = self.seats[18:]
        self.wchb_neigh = dict()
        for s in self.wchb_seats :
            if s%6 == 2 or s%6 == 5 and s//6 > 2:
                self.wchb_neigh[s] = self.add_seats([s-1, s+1, s-6-1, s-6+1, s-12-1, s-12+1, s-18-1, s-18+1])

        self.business_seats = [k for k in range(1, 6*business_line_bound+1)]    

        self.business_neigh = dict()
        for s in self.business_seats:
            if s%6 == 3 or s%6 == 0:
                self.business_neigh[s] = self.add_seats([s-1])
            if s%6 == 4 or s%6 == 1:
                self.business_neigh[s] = self.add_seats([s+1])
            else :
                self.business_neigh[s] = self.add_seats([s-1, s+1])
        
        alley_size = 2
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
        self.center_zone = self.add_seats([nb_line//2*6 + 2 - 12, nb_line//2*6 + 3 - 12, nb_line//2*6 + 2 + 12, nb_line//2*6 + 3 + 12])
        


        self.a = self.seat_position

    