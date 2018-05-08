import tornado.ioloop
import tornado.web

from config.foos_config import RESULTS_FILE_NAME

import json

from League import League

try:
    with open(RESULTS_FILE_NAME) as og_results:
        league = League.from_results_csv(og_results)
except IOError:
    with open('data/original_results.csv') as og_results:
        league = League.from_results_csv(og_results)

# Everything in here is sort of weirdly abstracted because of the idea that this might
# one day keep track of multiple leagues at once. e.g. if a large simulation is run in
# a secondary league instance
def save_league(file_name=RESULTS_FILE_NAME):
    league.export_to_csv(elos=False, file_name=file_name)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(league.stat_report())

class EloHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self):
        self.write(league.elo_history_json())

class FullGameHistoryHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({'games': league.game_history_json()})

class PlayRoundRobinHandler(tornado.web.RequestHandler):
    def post(self):
        round_robin_games = league.play_round_robin()

        self.write({'games': [game.to_json(verbose_players=True) for game in round_robin_games]})

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/api/elos", EloHandler),
        (r"/api/gamehistory", FullGameHistoryHandler),
        (r"/api/roundrobin", PlayRoundRobinHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(5000)
    print("listening on port 5000")
    tornado.ioloop.IOLoop.current().start()