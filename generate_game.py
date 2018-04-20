from poisson import poisson_sample
from random import random

# This is a function that will take two players and generate a game.
def generate_game(player_a, player_b):
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