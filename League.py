import csv
from Player import Player

# This is a move toward a little more OO instead of dicts everywhere.

# This is a League Class

class League:
    # players = [] # this would be shared by all instances of League
    def __init__(self, players, game_rows): # first argument to methods is self
        self.players = players
        self.games = []
        
        for game_row in game_rows:
            game = self.transform_game_row(game_row)
            self.add_game_to_league(game["score_tuple_a"], game["score_tuple_b"], game["date"])
    
    @classmethod
    def from_results_csv(cls, results_csv):
        # Could use input validation but this isn't client side soooo
        contents = list(csv.reader(results_csv))
        headers = contents[0]
        # players = headers[2:]
        player_names = headers[2:]
        games = contents[1:]
        # stats = Stats(players, games)
        players = [Player(pname) for pname in player_names]
        return cls(players, games)
    
    def add_game_to_league(self, score_tuple_a, score_tuple_b, date):
        self.update_stats
        self.games.append({
            "score_tuple_a":score_tuple_a,
            "score_tuple_b":score_tuple_b,
            "date": date
        })

    def update_stats(self, score_tuple_a, score_tuple_b):
        pass


    # This will take a "score marquee array" and transform it to (player_id, score) pairs in a dict with metadata
    @staticmethod
    def transform_game_row(game_result):

        # All fields of game_result are strings
        game_date = int(game_result[1]) # formatting this later
        
        scores = game_result[2:]
        # Generate a tuple (player_id, score)
        game_player_scores = []
        for index in range(len(scores)):
            if scores[index] != '': # this player #index was in the game
                game_player_scores.append((index, int(scores[index])))
        
        return {
            "date": game_date,
            "score_tuple_a": game_player_scores[0],
            "score_tuple_b": game_player_scores[1]
        }