import tornado.ioloop
import tornado.web

import json

from League import League

with open('data/original_results.csv') as og_results:
    league = League.from_results_csv(og_results)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(league.stat_report())

class EloHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(json.dumps(league.elo_history_json()))

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/api/elos", EloHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("listening on port 8888")
    tornado.ioloop.IOLoop.current().start()