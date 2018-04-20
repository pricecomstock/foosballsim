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
        player_names = headers[2:]
        games = contents[1:]
        players = [Player(pname) for pname in player_names]
        return cls(players, games)
    
    def add_game_to_league(self, score_tuple_a, score_tuple_b, date):
        self.update_stats(score_tuple_a, score_tuple_b)
        self.games.append({
            "score_tuple_a":score_tuple_a,
            "score_tuple_b":score_tuple_b,
            "date": date
        })

    def update_stats(self, score_tuple_a, score_tuple_b): 
        player_a = self.players[score_tuple_a[0]] # get player from index included in tuple
        player_b = self.players[score_tuple_b[0]] # get player from index included in tuple

        first_game = len(self.games) == 0
        if first_game: # if it's the first game, the winner will be king
            player_a_king = True
            player_b_king = True
        else:
            player_a_king = player_a.king
            player_b_king = player_b.king

        player_a.update_stats(own_points=score_tuple_a[1], opp_points=score_tuple_b[1], opp_king=player_b_king, opp_elo=player_b.elo)
        player_b.update_stats(own_points=score_tuple_b[1], opp_points=score_tuple_a[1], opp_king=player_a_king, opp_elo=player_a.elo)


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