import unittest
from League import League
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
            "date": 41780,
            "score_tuple_a": (0, 2),
            "score_tuple_b": (1, 4)
        })
    
    def test_game_add(self):
        with open('original_results.csv') as og_results:
            test_league = League.from_results_csv(og_results)
        test_league.add_game_to_league((0,3), (2,5), 41780)
        self.assertEqual(test_league.games[-1], {
            "date": 41780,
            "score_tuple_a": (0, 3),
            "score_tuple_b": (2, 5)
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

class TestLeagueGames(unittest.TestCase):
    
    def test_stat_updates(self):
        with open('original_results.csv') as og_results:
            test_league = League.from_results_csv(og_results)
        
        p0_prev_wins = test_league.players[0].wins
        p1_prev_losses = test_league.players[1].losses
        test_league.add_game_to_league((0,3), (1,2), 41780)
        
        self.assertEqual(test_league.players[0].wins, 1 + p0_prev_wins)
        self.assertEqual(test_league.players[1].losses, 1 + p1_prev_losses)
        

if __name__ == '__main__':
    unittest.main()