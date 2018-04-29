from Player import Player
from PlayerSnapshot import PlayerSnapshot
from poisson import poisson_sample
from random import random
from datetime import datetime, date, timedelta

class Game:
    
    def __init__(self, player_a, player_b, score_a, score_b, overtime, first_game=False, date=date.today()):
        self.overtime = overtime
        self.score_a = score_a
        self.score_b = score_b
        self.date = date

        if first_game: # if it's the first game, the winner will be king
            player_a_king = True
            player_b_king = True
        else:
            player_a_king = player_a.king
            player_b_king = player_b.king
        
        player_a_elo = player_a.elo
        player_b_elo = player_b.elo

        # update both players stats atomically
        player_a.update_stats(score_a, score_b, player_b_king, player_b_elo)
        player_b.update_stats(score_b, score_a, player_a_king, player_a_elo)

        self.player_a_snapshot = PlayerSnapshot(player_a)
        self.player_b_snapshot = PlayerSnapshot(player_b)

        if player_a_king != player_a.king or player_b_king != player_b.king:
            self.king_change = True
        else:
            self.king_change = False

    @classmethod
    def generate_random_from_players(cls, player_a, player_b):
        score_a, score_b, overtime = cls.generate_scores(player_a, player_b)
        return cls(player_a, player_b, score_a, score_b, overtime)
    
    @classmethod
    def create_from_scores(cls, player_a, player_b, score_a, score_b, overtime=False, first_game=False, date=date.today()):
        return cls(player_a, player_b, score_a, score_b, overtime, first_game, date)
    
    @staticmethod
    def generate_scores(player_a, player_b):
        player_a_lambd = (player_a.avg_points_scored + player_b.avg_points_allowed) / 2.0
        player_b_lambd = (player_b.avg_points_scored + player_a.avg_points_allowed) / 2.0

        player_a_score = poisson_sample(player_a_lambd)
        player_b_score = poisson_sample(player_b_lambd)

        overtime = False
        if player_a_score == player_b_score:
            overtime = True
            # Calculate extra point proportionally to lambda
            if random() * (player_a_lambd + player_b_lambd) < player_a_lambd:
                player_a_score += 1
            else:
                player_b_score += 1
        
        return (player_a_score, player_b_score, overtime)
    
    def stateless_report(self): # A report that ignores any league stuff and player stats
        return "DATE:{}, {}: {}\n{}: {}".format(self.date, self.player_a_snapshot.name, self.score_a,
            self.player_b_snapshot.name, self.score_b)
    
    def get_winner_loser(self):
        if self.score_a > self.score_b:
            return (self.player_a_snapshot, self.player_b_snapshot, self.score_a, self.score_b)
        else:
            return (self.player_b_snapshot, self.player_a_snapshot, self.score_b, self.score_a)

    def game_description_report(self):
        winner, loser, score_winner, score_loser = self.get_winner_loser()
        if self.king_change:
            king_string = 'to become king'
        else:
            king_string = ''
        return "{} defeats {} {}-{} {}".format(winner.name, loser.name, str(score_winner), str(score_loser), king_string)