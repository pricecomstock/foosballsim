# This is a Stats object

class Player:

    def __init__(self, name): # first argument to methods is self
        self.name = name
        self.wins = 0
        self.losses = 0
        self.winning_run = False
        self.run = 0
        self.avg_points_scored = 0
        self.avg_points_allowed = 0
        self.avg_margin_victory = 0
        self.avg_margin_loss = 0
        self.win_percent = 0.0
        self.elo = 1000
        self.king = False
