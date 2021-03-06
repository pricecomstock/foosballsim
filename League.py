import csv
from datetime import datetime, date, timedelta

from itertools import combinations

from Game import Game
from Player import Player

from config.foos_config import STARTING_ELO

# This is a League Class


class StaticLeagueModifyException(Exception):
    def __init__(self, message):
        self.message = message

class League:
    # players = [] # this would be shared by all instances of League
    def __init__(self, players, game_rows, static_league): # first argument to methods is self
        self.players = players
        self.games = []
        self.static_league = False
        
        first_game = True
        for game_row in game_rows:
            self.add_game_from_row(game_row, first_game)
            first_game = False # only the first game should be the first game, duh
        
        self.static_league = static_league
        
    
    @classmethod
    def from_results_csv(cls, results_csv, static_league=False):
        contents = list(csv.reader(results_csv))
        headers = contents[0]
        player_names = headers[2:]
        game_rows = contents[1:]
        players = [Player(pname) for pname in player_names]
        return cls(players, game_rows, static_league)

    def play_generated_game(self, player_a_index, player_b_index):

        player_a = self.players[player_a_index]
        player_b = self.players[player_b_index]
        
        game = Game.generate_random_from_players(player_a, player_b, game_number=len(self.games) + 1)
        
        if not self.static_league:
            self.games.append(game)
        
        return game
    
    def play_round_robin(self):
        indices_to_play = list(combinations(range(len(self.players)), 2)) # every 2 player match possible

        # def kingsort(player_indices):
        #     return 1 if self.players[player_indices[0]].king or self.players[player_indices[1]].king else 0

        # indices_to_play.sort(kingsort) # King goes last

        # TODO: make it so that players go in order of round robin winpct against king

        round_robin_games = []

        for player_a_index, player_b_index in indices_to_play:
            game = self.play_generated_game(player_a_index, player_b_index)
            round_robin_games.append(game)
        
        return round_robin_games
    
    def play_generated_game_by_player_names(self, player_a, player_b):
        lowercase_players = [player.name.lower() for player in self.players]

        try:
            player_a_index = lowercase_players.index(player_a.lower())
            player_b_index = lowercase_players.index(player_b.lower())
        except ValueError:
            return None

        game = self.play_generated_game(player_a_index, player_b_index)
        
        return game

    def stat_report(self):
        def elo_sort_function(player):
            return player.elo

        elo_sorted_players = sorted(self.players, key=elo_sort_function, reverse=True)

        report = ''
        report += Player.str_header() + '\n'
        report += '\n'.join([str(player) for player in elo_sorted_players])
        return report

    # This will take a "score marquee array" and transform it to (player_id, score) pairs in a dict with metadata
    def add_game_from_row(self, game_result, first_game=False):
        if self.static_league:
            raise StaticLeagueModifyException("Cannot add games to static league!")
        else:
            # All fields of game_result are strings
            td = timedelta(days=int(game_result[1])-1)
            game_date = date(1900,1,1) + td
            
            scores = game_result[2:]

            # Generate a tuple (player_id, score)
            game_player_scores = []
            for index in range(len(scores)):
                if scores[index] != '': # this player #index was in the game
                    game_player_scores.append((index, int(scores[index])))
            
            game = self.add_game_from_index_score_tuples(game_player_scores[0], game_player_scores[1], date=game_date)
            return game
    
    def add_game_from_index_score_tuples(self, player_a_score_tuple, player_b_score_tuple, date=date.today()):
        if self.static_league:
            raise StaticLeagueModifyException("")
        else:
            player_a = self.players[player_a_score_tuple[0]]
            player_b = self.players[player_b_score_tuple[0]]
            if len(self.games) == 0:
                first_game = True
            else:
                first_game = False
            game = Game.create_from_scores(player_a, player_b, player_a_score_tuple[1], player_b_score_tuple[1], date=date, first_game=first_game, game_number=len(self.games) + 1)
            self.games.append(game)
            return game
    
    def export_to_csv(self, elos=False, file_name='test_output/' + date.today().isoformat() + 'test.csv'):
        with open(file_name, 'w') as csvfile:
            field_names = ["Game", "Date"]
            field_names += [player.name for player in self.players]
            if elos:
                field_names += [player.name + "_elo" for player in self.players]

            writer = csv.writer(csvfile)
            writer.writerow(field_names)
            if elos:
                elos = [STARTING_ELO for x in range(len(self.players))]
            for index, game in enumerate(self.games):
                game_date = (game.date - date(1900,1,1)).days + 1
                row = [index+1, game_date]
                
                player_a_index = self.get_player_index_by_name(game.player_a_snapshot.name)
                player_b_index = self.get_player_index_by_name(game.player_b_snapshot.name)

                scores = [None for x in range(len(self.players))]
                scores[player_a_index] = game.score_a
                scores[player_b_index] = game.score_b

                row += scores
                
                if elos:
                    elos[player_a_index] = game.player_a_snapshot.elo
                    elos[player_b_index] = game.player_b_snapshot.elo

                    row += elos
                writer.writerow(row)
            
            return file_name
    
    def get_player_index_by_name(self, name):
        for index, player in enumerate(self.players):
            if player.name == name:
                return index
    
    def elo_history_array(self):
        player_names = [player.name for player in self.players]
        elos = []
        for game in self.games:
            winner, loser, score_winner, score_loser = game.get_winner_loser()
            elo_change = game.elo_change
            
            elo_diff = [0] * len(self.players) # array of zeroes. non participants have no diff
            elo_diff[player_names.index(winner.name)] = elo_change # winner gains elo
            elo_diff[player_names.index(loser.name)] = 0 - elo_change # loser loses elo

            if len(elos) == 0:
                previous_elos = [STARTING_ELO] * len(self.players)
            else:
                previous_elos = elos[-1]
            
            elos.append([previous + change for previous, change in zip(previous_elos, elo_diff)])
        
        return elos
    
    def elo_history_json(self):
        player_names = [player.name for player in self.players]
        elos = self.elo_history_array()
        return {
            "players": player_names,
            "elos": elos
        }
    
    def game_history_json(self, start_index=0, end_index=None):
        if end_index == None:
            end_index = len(self.games) - 1
        
        return [game.to_json(verbose_players=True) for game in self.games[start_index:end_index]]

    def summaryJson(self):
        return {
            'games': len(self.games),
            'players': len(self.players),
        }
    

    def slack_report(self):
        return {
            'text': 'STAT REPORT: ```' + self.stat_report() + '```'
        }