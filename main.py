import tornado.ioloop
import tornado.web

from config.foos_config import DEFAULT_LEAGUE_INPUT_FILES
from config.webhook_config import NOTIFIERS

import json

from League import League

leagues = {}
league_notifiers = {}

for league_name in DEFAULT_LEAGUE_INPUT_FILES:
    try:
        with open(DEFAULT_LEAGUE_INPUT_FILES[league_name]['input_file']) as original_results:
            # { league_name: LeagueObject }
            leagues.setdefault(league_name, League.from_results_csv(original_results, static_league=DEFAULT_LEAGUE_INPUT_FILES[league_name]['static']))
    except IOError:
        pass

for notifier in NOTIFIERS:
    for league_name in leagues:
        if league_name in notifier['leagues']:
            league_notifiers.setdefault(league_name, [])
            league_notifiers[league_name].append((notifier['game_notifier'], notifier['league_notifier']))

# This would be a little more elegant with a database at this point but MVP!!!
def save_league(league_name):
    leagues[league_name].export_to_csv(elos=False, file_name='results/' + league_name + ".csv")
    # pass

class LeagueListHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'GET')

    def get(self):
        # e.g. {'players': 3, 'games': 470, 'name': 'og'}
        league_list = []

        # This is gross and I should probably make an object to keep track of all the leagues
        for league_name in leagues:
            summary = leagues[league_name].summaryJson()
            summary.update({'name': league_name})
            league_list.append(summary)
        self.write({"leagues": league_list})

class EloHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'GET')

    def get(self, league_name):
        self.write(leagues[league_name].elo_history_json())

class FullGameHistoryHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'GET')

    def get(self, league_name):
        self.write({'games': leagues[league_name].game_history_json()})

class PlayRoundRobinHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'GET')

    def post(self, league_name):
        if league_name in leagues:
            round_robin_games = leagues[league_name].play_round_robin()

            if league_name in league_notifiers: # is there a notifier on this league?
                for game_notifier, league_notifier in league_notifiers[league_name]:
                    for game in round_robin_games:
                        game_notifier(game)
                    league_notifier(leagues[league_name])
            
            if not leagues[league_name].static_league:
                save_league(league_name)

            self.write({'games': [game.to_json(verbose_players=True) for game in round_robin_games]})
        else:
            self.write({'success': False, 'error': 'league not found'})

class SlackGameRequestHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'GET')

    def post(self):
        data = self.get_body_argument("text", default=None, strip=True)
        league_name = 'the-eternal-season'

        if data.lower() in ['table', 'stats']:
            self.write(leagues[league_name].slack_report())
            return
        
        if data is not None and len(data.split()) == 2:
            player_a, player_b = data.split()
        else:
            self.write({'response_type': 'ephemeral', 'text': 'you fucked this up somehow'})
            return
        

        if league_name in leagues:
            game = leagues[league_name].play_generated_game_by_player_names(player_a, player_b)

            if game is not None:
                if not leagues[league_name].static_league:
                    save_league(league_name)

                slack_report = game.slack_report()
                slack_report['response_type'] = 'in_channel'
                
                self.write(slack_report)
            
            else:
                self.write({'response_type': 'ephemeral', 'text': 'those are not real players'})
        else:
            self.write({'response_type': 'ephemeral', 'text': 'league not found'})

def make_app():
    return tornado.web.Application([
        (r"/api/listleagues", LeagueListHandler),
        (r"/api/elos/(.*)", EloHandler),
        (r"/api/gamehistory/(.*)", FullGameHistoryHandler),
        (r"/api/roundrobin/(.*)", PlayRoundRobinHandler),
        (r"/api/slackgamerequest", SlackGameRequestHandler),
        (r'/(.*)', tornado.web.StaticFileHandler, {'path': 'static/', "default_filename": "index.html"}),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(5000)
    print("listening on port 5000")
    tornado.ioloop.IOLoop.current().start()