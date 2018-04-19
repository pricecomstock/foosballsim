# This is a Player object
from elo import elo_change

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
        self.update_wins_losses(own_points, opp_points)
        self.update_run(own_points, opp_points)
        self.update_points_scored_allowed_total(own_points, opp_points)
        self.update_margin_total(own_points, opp_points)
        self.update_elo(own_points, opp_points, opp_elo)

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
        self.avg_points_scored = self.total_points_scored / (self.wins + self.losses)
        self.avg_points_allowed = self.total_points_allowed / (self.wins + self.losses)
        self.avg_margin_victory = self.total_margin_victory / self.wins
        self.avg_margin_loss = self.total_margin_loss / self.losses