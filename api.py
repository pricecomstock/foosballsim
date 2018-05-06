import tornado.ioloop
import tornado.web

from League import League

with open('data/original_results.csv') as og_results:
    league = League.from_results_csv(og_results)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(league.stat_report())

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()