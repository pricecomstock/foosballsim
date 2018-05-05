import csv
from datetime import datetime, date, timedelta

from Game import Game
from Player import Player

from config.foos_config import STARTING_ELO

# This is a League Class

class League:
    # players = [] # this would be shared by all instances of League
    def __init__(self, players, game_rows): # first argument to methods is self
        self.players = players
        self.games = []
        
        first_game = True
        for game_row in game_rows:
            self.add_game_from_row(game_row, first_game)
            first_game = False # only the first game should be the first game, duh
    
    @classmethod
    def from_results_csv(cls, results_csv):
        contents = list(csv.reader(results_csv))
        headers = contents[0]
        player_names = headers[2:]
        game_rows = contents[1:]
        players = [Player(pname) for pname in player_names]
        return cls(players, game_rows)

    def play_generated_game(self, player_a_index, player_b_index):
        player_a = self.players[player_a_index]
        player_b = self.players[player_b_index]
        
        game = Game.generate_random_from_players(player_a, player_b)
        self.games.append(game)
        
        return (game)
    
    def stat_report(self):
        report = ''
        report += self.players[0].str_header() + '\n'
        report += '\n'.join([str(player) for player in self.players])
        return report

    # This will take a "score marquee array" and transform it to (player_id, score) pairs in a dict with metadata
    def add_game_from_row(self, game_result, first_game=False):

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
        player_a = self.players[player_a_score_tuple[0]]
        player_b = self.players[player_b_score_tuple[0]]
        if len(self.games) == 0:
            first_game = True
        else:
            first_game = False
        game = Game.create_from_scores(player_a, player_b, player_a_score_tuple[1], player_b_score_tuple[1], date=date, first_game=first_game)
        self.games.append(game)
        return game
    
    def export_to_csv(self, elos=False, file_name=date.today().isoformat() + '-league.csv'):
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