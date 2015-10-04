#!/usr/bin/env python2

from flask import Flask
import json
import w2v_associations as associations

app = Flask(__name__)
model = associations.W2V()


@app.route(r'/<word>', methods=['GET'])
def analyze(word):
    return json.dumps(model.get_similair(word))

if __name__ == '__main__':
    app.run()
