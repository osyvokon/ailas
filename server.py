#!/usr/bin/env python3
import datetime
import random
from collections import Counter
from flask import Flask, request, jsonify as flask_jsonify
from pymongo import MongoClient


def jsonify(obj):
    if '_id' in obj:
        del obj['_id']
    return flask_jsonify(obj)


from build_dict import Corpora

c = Corpora()
app = Flask(__name__)
db = MongoClient().ailas

def get_hints(word):
    """Return list of terms describing the word. """

    if not word:
        return []

    return list(c.find_token_sentences(word))

def guess_by_hints(hints):

    candidates = Counter()
    for hint in hints:
        candidates.update(c.guess_candidates(hint))

    for h in hints:
        candidates[c.l.lemma(h)] = 0
    print (candidates)
    return [c for c, _ in candidates.most_common(30)]

@app.route('/api/get_hint/<session_id>')
def api_get_hint(session_id):
    # TODO: get hint by request
    session = db.sessions.find({'id': session_id})
    current_hint_id = session['current_hint_id'] + 1
    try:
        hint = session['hints'][current_hint_id]
    except Exception:
        return flask_jsonify({'hint': 'Нажаль все використані всі можливі підказки.'})
    db.sessions.update({'id', session_id},
                       {'$set': {'current_hint_id': current_hint_id}})
    return flask_jsonify({'hint': hint})

@app.route('/api/session', methods=['GET'])
def api_session_list():
    return jsonify({
        "sessions": list(db.sessions.find({'active': True}, fields={'_id': 0}))
    })

@app.route('/api/session', methods=['POST', 'PUT'])
def api_session_start():
    # TODO: create word, addrs, hints, current_hint_id fields in sessions
    # TODO: generate hints list
    session_id = request.json['id']
    callback = request.json['callback']
    session = {
        'id': session_id,
        'callback': callback,
        'active': True
    }
    db.sessions.update({'id': session_id},
                       {'$set': session},
                       upsert=True)

    return jsonify(session)


@app.route('/api/session/<session_id>/say', methods=['POST', 'PUT'])
def api_say(session_id):
    msg = request.json['txt'].lower()
    user = request.json['person']

    print(msg, '-------')

    if msg.startswith("/guess "):
        msg = msg.partition(' ')[2]
        hint = guess_by_hints(msg.split())
    else:
        hint = random.choice(get_hints(msg) or ['(dunno)'])

    db.messages.insert({
        "sessionId": session_id,
        "user": user,
        "msg": msg,
        "dt": datetime.datetime.now()
    })

    return jsonify({"hint": hint})

@app.route('/api/session/<session_id>', methods=['DELETE'])
def api_session_delete(session_id):
    db.sessions.update({"id": session_id}, {'$set': {'active': False}})
    return jsonify({"ok": True})


@app.route('/')
def form():
    query = request.args.get('query')
    associations = get_hints(query)

    return """
<html>
<meta charset="utf-8">
<body>
    <form action="/" method="get">
        <input type="text" name="query" value="{query}" autofocus>
        <input type="submit" value="Submit">
    </form>

    <textarea rows=20 cols=80>{associations}</textarea>
</body>
</html>
""".format(associations='\n'.join(associations),
           query=query)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
