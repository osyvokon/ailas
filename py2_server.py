#!/usr/bin/env python2

import tornado.ioloop
import tornado.web
import json
from w2v_associations import W2V

analyzer = W2V()


class MainHandler(tornado.web.RequestHandler):
    def get(self, word):
        data = analyzer.get_similair(word)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(data))

application = tornado.web.Application([
    (r"/(.+)", MainHandler),
])

if __name__ == "__main__":
    application.listen(8888, address='0.0.0.0')
    tornado.ioloop.IOLoop.instance().start()
