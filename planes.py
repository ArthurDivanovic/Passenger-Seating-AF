class Plane:

    '[Explain Plane class]' 
    
    def get_column(self, seat_nb):
        return seat_nb%6
    
    def get_line(self, seat_nb):
        return seat_nb//6
    
    def __init__(self, nb_line=100, exit_lines=[], business_line_bound=0):
        
        self.nb_seat= nb_line * 6
        self.seats = [k for k in range(1, self.nb_seat+1)]
        self.emergency_seats = [6 * (line-1) + 1 for line in exit_lines] + [6 * line for line in exit_lines]
        
        self.alley_seats = []
        for s in self.seats :
            if s%6 == 3 or s%6 == 4:
                self.alley_seats.append(s)
        
        self.child_neigh = []
        for s in self.seats:
            if s%6 == 3 or s%6 == 0:
                self.child_neigh.append([s-1])
            if s%6 == 4 or s%6 == 1:
                self.child_neigh.append([s+1])
            else :
                self.child_neigh.append([s-1, s+1])

        self.wchr_neigh = []
        for s in self.alley_seats:
            if s%6 == 3:
                self.wchr_neigh.append([s-6, s-6+1, s+1])
            if s%6 == 4:
                self.wchr_neigh.append([s-6, s-6-1, s-1])

        self.wchb_neigh = []
        for s in self.seats:
            if s%6 == 2 or s%6 == 5 and s//6 > 2:
                self.wchb_neigh.append([s-1, s+1, s-6-1, s-6+1, s-12-1, s-12+1, s-18-1, s-18+1, s-24-1, s-24+1])

        self.business_seats = [k for k in range(1, 6*business_line_bound+1)]    
    
    