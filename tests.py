import unittest
from League import League

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
        

if __name__ == '__main__':
    unittest.main()