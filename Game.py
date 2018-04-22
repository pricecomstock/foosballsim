from Player import Player
from poisson import poisson_sample
from random import random

class Game:
    
    def __init__(self, player_a, player_b, score_a, score_b, overtime):
        self.overtime = overtime

    @classmethod
    def generate_random_from_players(cls, player_a, player_b):
        player_a_score, player_b_score, overtime = cls.generate_scores(player_a, player_b)
        return cls(player_a, player_b, player_a_score, player_b_score, overtime)
    
    @classmethod
    def create_from_scores(cls, player_a, player_b, score_a, score_b):
        return cls(player_a, player_b, score_a, score_a, overtime)
    
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