import unittest
from datetime import date
from League import League
from Game import Game
from Player import Player, InvalidScoreError, InvalidKingError

class TestCSVImport(unittest.TestCase):

    def test_league_creation(self):
        with open('original_results.csv') as og_results:
            test_league = League.from_results_csv(og_results)
        self.assertIsInstance(test_league, League)
    
    def test_players(self):
        with open('original_results.csv') as og_results:
            test_league = League.from_results_csv(og_results)
        self.assertEqual([player.name for player in test_league.players], ['Price', 'Tritz', 'Elliott'])
    
    def test_game_transform(self):
        with open('original_results.csv') as og_results:
            test_league = League.from_results_csv(og_results)
        self.assertEqual(test_league.transform_game_row(['1','41780','2','4','']), {
            "date": date(2014, 5, 22),
            "score_tuple_a": (0, 2),
            "score_tuple_b": (1, 4)
        })
    
    def test_game_add(self):
        with open('original_results.csv') as og_results:
            test_league = League.from_results_csv(og_results)
        test_league.add_game_to_league((0,3), (2,5))
        self.assertEqual(test_league.games[-1], {
            "date": date.today(),
            "score_tuple_a": (0, 3),
            "score_tuple_b": (2, 5),
            "elos": [985.0615268063299, 1117.587679769858, 897.3507934238106]
        })

class TestPlayerAndStats(unittest.TestCase):
    def test_creation(self):
        test_player = Player('test')
        self.assertEqual(test_player.name, 'test')
        self.assertEqual(test_player.elo, 1000)

    def test_wins_losses(self):
        test_player = Player('test')
        self.assertEqual(test_player.wins, 0)
        self.assertEqual(test_player.losses, 0)

        test_player.update_wins_losses(1,0)
        test_player.update_wins_losses(1,0)
        self.assertEqual(test_player.wins, 2)
        self.assertEqual(test_player.losses, 0)

        test_player.update_wins_losses(0,1)
        test_player.update_wins_losses(0,1)
        self.assertEqual(test_player.wins, 2)
        self.assertEqual(test_player.losses, 2)
    
    def test_tie_rejection(self):
        test_player = Player('test')
        self.assertRaises(InvalidScoreError, test_player.update_stats, 5,5,True,1000)
    
    def test_run(self):
        test_player = Player('test')
        test_player.update_run(0, 1) # loss
        self.assertFalse(test_player.winning_run)
        self.assertEqual(test_player.run, 1)
        test_player.update_run(0, 1) # loss
        self.assertFalse(test_player.winning_run)
        self.assertEqual(test_player.run, 2)
        
        test_player.update_run(1, 0) # win
        self.assertTrue(test_player.winning_run)
        self.assertEqual(test_player.run, 1)
        test_player.update_run(1, 0) # win
        test_player.update_run(1, 0) # win
        test_player.update_run(1, 0) # win
        self.assertTrue(test_player.winning_run)
        self.assertEqual(test_player.run, 4)
    
    def test_point_stats_totals(self):
        test_player = Player('test')
        test_player.update_stats(1,5,True,1000)
        test_player.update_stats(5,2,False,1000)

        self.assertEqual(test_player.total_margin_victory, 3)
        self.assertEqual(test_player.total_margin_loss, 4)
        self.assertEqual(test_player.total_points_scored, 6)
        self.assertEqual(test_player.total_points_allowed, 7)
    
    def test_point_stats_avg(self):
        test_player = Player('test')
        test_player.update_stats(1,5,True,1000)
        test_player.update_stats(5,2,False,1000)

        self.assertEqual(test_player.avg_margin_victory, 3)
        self.assertEqual(test_player.avg_margin_loss, 4)
        self.assertEqual(test_player.avg_points_scored, 3)
        self.assertEqual(test_player.avg_points_allowed, 3.5)
        
        test_player.update_stats(10,4,False,1000)
        test_player.update_stats(2,3,False,1000)

        self.assertEqual(test_player.avg_margin_victory, 4.5)
        self.assertEqual(test_player.avg_margin_loss, 2.5)
        self.assertEqual(test_player.avg_points_scored, 4.5)
        self.assertEqual(test_player.avg_points_allowed, 3.5)
    
    def test_win_percent(self):
        test_player = Player('test')
        test_player.update_stats(5,2,False,1000)
        self.assertAlmostEqual(test_player.win_percent, 1.0)
        test_player.update_stats(1,5,False,1000)
        self.assertAlmostEqual(test_player.win_percent, 0.5)
        test_player.update_stats(5,2,False,1000)
        self.assertAlmostEqual(test_player.win_percent, 0.666666667)

    def test_elo(self):
        test_player = Player('test')
        test_player.update_elo(1, 0, 1000)
        self.assertNotEqual(test_player.elo, 1000)
        self.assertEqual(test_player.elo, 1025)
        test_player.update_elo(0, 1, 1025)
        self.assertEqual(test_player.elo, 1000)

    def test_king_duplicate_rejection(self):
        test_player = Player('test')
        test_player.update_stats(5,2,True,1000)
        self.assertRaises(InvalidKingError, test_player.update_stats, 5,3,True,1000) # but i'm the king!
    
    def test_king(self):
        test_player = Player('test')
        test_player.update_stats(5,2,True,1000) # becomes king
        self.assertTrue(test_player.king)
        test_player.update_stats(5,2,False,1000) # remains king
        self.assertTrue(test_player.king)
        test_player.update_stats(2,5,False,1000) # loses king
        self.assertFalse(test_player.king)
        test_player.update_stats(5,2,False,1000) # remains NOT king
        self.assertFalse(test_player.king)

class TestGames(unittest.TestCase):
    def test_random_game(self):
        with open('original_results.csv') as og_results:
            test_league = League.from_results_csv(og_results)
        
        player_a, player_b = test_league.players[0:1]
        game = Game.generate_random_from_players(player_a, player_b)
        
        self.assertGreaterEqual(game.score_a, 0)
        self.assertGreaterEqual(game.score_b, 0)
        self.assertIsNotNone(game.overtime)

class TestLeagueGames(unittest.TestCase):
    
    def test_stat_updates(self):
        with open('original_results.csv') as og_results:
            test_league = League.from_results_csv(og_results)
        
        p0_prev_wins = test_league.players[0].wins
        p1_prev_losses = test_league.players[1].losses
        test_league.add_game_to_league((0,3), (1,2), 41780)
        
        self.assertEqual(test_league.players[0].wins, 1 + p0_prev_wins)
        self.assertEqual(test_league.players[1].losses, 1 + p1_prev_losses)
    
    def test_imported_stats(self):
        with open('original_results.csv') as og_results:
            test_league = League.from_results_csv(og_results)
        
        price = test_league.players[0]
        tritz = test_league.players[1]
        elliott = test_league.players[2]

        self.assertEqual(price.wins, 77+42)
        self.assertEqual(price.losses, 151+68)
        self.assertFalse(price.winning_run)
        self.assertAlmostEqual(price.elo, 1024.5495720207086, 3)
        self.assertFalse(price.king)

        self.assertEqual(tritz.wins, 151+97)
        self.assertEqual(tritz.losses, 77+36)
        self.assertAlmostEqual(tritz.elo, 1117.587679769858, 3)
        self.assertTrue(tritz.king)
 
        self.assertEqual(elliott.wins, 68+36)
        self.assertEqual(elliott.losses, 42+97)
        self.assertAlmostEqual(elliott.elo, 857.8627482094315, 3)
        self.assertFalse(elliott.king)

    def test_generated_games(self):
        with open('original_results.csv') as og_results:
            test_league = League.from_results_csv(og_results)
        
        results = test_league.play_generated_game(0,1)
        self.assertNotEqual(results[0], None)
        self.assertNotEqual(results[1], None)
        self.assertNotEqual(results[2], None)
        self.assertNotEqual(results[3], None)

class TestCSVExport(unittest.TestCase):

    def test_no_elo_export(self):
        with open('original_results.csv') as og_results:
            test_league = League.from_results_csv(og_results)
        
        with open('original_results.csv') as og_results:
            og_results_list = list(og_results)

        test_file = test_league.export_to_csv()
        print("opening" + test_file)
        with open(test_file) as test_results:
            test_results_list = list(test_results)
        
        self.assertListEqual(og_results_list, test_results_list)

        


if __name__ == '__main__':
    unittest.main()