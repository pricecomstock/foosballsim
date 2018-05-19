from Player import Player
from PlayerSnapshot import PlayerSnapshot
from league_math.poisson import poisson_sample
from random import random
from datetime import datetime, date, timedelta

class Game:
    
    def __init__(self, player_a, player_b, score_a, score_b, overtime, first_game=False, date=date.today(), game_number = None):
        self.game_number = game_number

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

        self.elo_change = abs(player_a.elo - player_a_elo)

        self.player_a_snapshot = PlayerSnapshot(player_a)
        self.player_b_snapshot = PlayerSnapshot(player_b)

        if player_a_king != player_a.king or player_b_king != player_b.king:
            self.king_change = True
        else:
            self.king_change = False

    @classmethod
    def generate_random_from_players(cls, player_a, player_b, game_number=None):
        score_a, score_b, overtime = cls.generate_scores(player_a, player_b)
        return cls(player_a, player_b, score_a, score_b, overtime, game_number=game_number)
    
    @classmethod
    def create_from_scores(cls, player_a, player_b, score_a, score_b, overtime=False, first_game=False, date=date.today(), game_number=None):
        return cls(player_a, player_b, score_a, score_b, overtime, first_game, date, game_number=game_number)
    
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

        king_string = ' to become king' if self.king_change else ''
        overtime_string = ' in sudden death' if self.overtime else ''
        
        return "GAME #{}: *{}* defeats *{}* {}-{}{}{}!".format(str(self.game_number), winner.name, loser.name, str(score_winner), str(score_loser), overtime_string, king_string)
    
    def to_json(self, verbose_players=False):
        winner, loser, score_winner, score_loser = self.get_winner_loser()

        return {
            'winner': {
                'player': winner.to_json() if verbose_players else winner.name,
                'score': score_winner
            },
            'loser': {
                'player': loser.to_json() if verbose_players else loser.name,
                'score': score_loser
            },
            'date': self.date.toordinal(),
            'overtime': self.overtime,
            'kingChange': self.king_change,
            'eloChange': self.elo_change
        }
    
    def slack_report(self):
        # TODO: Extract this and attach it to player objects and send it to front end so there's a single source of truth
        color_map = {
            'Price': '#66D',
            'Tritz': '#D66',
            'Elliott': '#8C8',
            'Mark': '#B82',
            'Joe': '#ADF',
            'Erick': '#FA4',
            'Bijan': '#C7D',
            'Harsh': '#FAF'
        }

        report = self.game_description_report()
        winner, loser, score_winner, score_loser = self.get_winner_loser()
        summary_template = '{0} - {1} [{2:.1f}-->{3:.1f} | {4:+.1f}]'
        winner_summary = summary_template.format(score_winner, winner.name, winner.elo - self.elo_change, winner.elo, self.elo_change)
        loser_summary = summary_template.format(score_loser, loser.name, loser.elo + self.elo_change, loser.elo, self.elo_change)
        return {
            'text':report,
            'attachments':[
                {
                    'color': color_map[winner.name],
                    'fallback': report,
                    'fields':[
                        {
                            'title': winner_summary,
                            'value': ':soccer:'*score_winner,
                            'short': False
                        },
                        {
                            'title': loser_summary,
                            'value': ':soccer:'*score_loser,
                            'short': False
                        }
                    ]
                }
            ]
        }