# This is a Player object
from elo import elo_change

class InvalidScoreError(Exception):
    pass

class InvalidKingError(Exception):
    pass

class Player:
    
    def __init__(self, name): # first argument to methods is self
        self.name = name
        
        self.wins = 0
        self.losses = 0
        
        self.winning_run = False
        self.run = 0

        self.total_points_scored = 0
        self.avg_points_scored = 0.0
        self.total_points_allowed = 0
        self.avg_points_allowed = 0.0
        
        self.total_margin_victory = 0
        self.avg_margin_victory = 0.0
        self.total_margin_loss = 0
        self.avg_margin_loss = 0.0

        self.win_percent = 0.0
        self.elo = 1000
        self.king = False

    def update_stats(self, own_points, opp_points, opp_king, opp_elo):
        if own_points == opp_points:
            raise InvalidScoreError("Tie games are not allowed")
        
        if own_points < 0 or opp_points < 0:
            raise InvalidScoreError("Negative scores are not allowed")
        
        if self.king and opp_king:
            raise InvalidKingError("The opponent said they were the king but I'm the king!")
        
        self.update_wins_losses(own_points, opp_points)
        self.update_run(own_points, opp_points)
        self.update_points_scored_allowed_total(own_points, opp_points)
        self.update_margin_total(own_points, opp_points)
        self.update_elo(own_points, opp_points, opp_elo)
        self.update_king(own_points, opp_points, opp_king)

        self.update_win_percent()
        self.update_averages()
    
    def update_wins_losses(self, own_points, opp_points):
        if own_points > opp_points:
            self.wins += 1
        else:
            self.losses += 1
    
    def update_run(self, own_points, opp_points):
        if self.winning_run: #already on winning run
            if own_points > opp_points:
                self.run += 1
            else:
                self.winning_run = False
                self.run = 1
        else: #already on losing run
            if own_points > opp_points:
                self.winning_run = True
                self.run = 1
            else:
                self.run += 1
    
    def update_points_scored_allowed_total(self, own_points, opp_points):
        self.total_points_scored += own_points
        self.total_points_allowed += opp_points
    
    def update_margin_total(self, own_points, opp_points):
        if own_points > opp_points:
            self.total_margin_victory += own_points - opp_points
        else:
            self.total_margin_loss += opp_points - own_points
    
    def update_elo(self, own_points, opp_points, opp_elo):
        self.elo = elo_change(self.elo, opp_elo, own_points, opp_points)[0]
    
    def update_averages(self):
        if self.wins == 0: # it's possible to still have zero has divisor if you haven't one a game
            self.avg_margin_victory = 0.0
        else:
            self.avg_margin_victory = self.total_margin_victory / float(self.wins)
        
        if self.losses == 0:
            self.avg_margin_loss = 0.0
        else:
            self.avg_margin_loss = self.total_margin_loss / float(self.losses)

        self.avg_points_scored = self.total_points_scored / float(self.wins + self.losses)
        self.avg_points_allowed = self.total_points_allowed / float(self.wins + self.losses)
    
    def update_win_percent(self):
        self.win_percent = self.wins / float(self.wins + self.losses)
    
    def update_king(self, own_points, opp_points, opp_king):
        won = own_points > opp_points
        if won and opp_king:
            self.king = True
        elif not won:
            self.king = False
    
    def str_header(self):
        return ''.join([
            'PLAYER'.ljust(8) + '|',
            'W'.rjust(5),
            'L'.rjust(5),
            'RUN'.rjust(4),
            'PS/G'.rjust(6),
            'PA/G'.rjust(6),
            'AM+'.rjust(6),
            'AM-'.rjust(6),
            'WIN%'.rjust(7),
            'ELO'.rjust(7),
            'KING'.rjust(5)
        ])

    def __str__(self):

        king_string = ''
        if self.king:
            king_string = ' K'
        
        if self.winning_run:
            run_string = 'W'
        else:
            run_string = 'L'
        
        return ''.join([
            self.name.ljust(8),
            '|',
            str(self.wins).rjust(5),
            str(self.losses).rjust(5),
            (str(self.run)+run_string).rjust(4),
            "{0:.2f}".format(self.avg_points_scored).rjust(6),
            "{0:.2f}".format(self.avg_points_allowed).rjust(6),
            "{0:.2f}".format(self.avg_margin_victory).rjust(6),
            "{0:.2f}".format(self.avg_margin_loss).rjust(6),
            "{0:.3f}".format(self.win_percent).rjust(7),
            "{0:.1f}".format(self.elo).rjust(7),
            king_string
        ])