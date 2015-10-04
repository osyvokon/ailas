#!/usr/bin/env python3
import datetime
import random
import urllib
import requests
from collections import Counter
from flask import Flask, request, jsonify as flask_jsonify
from pymongo import MongoClient


WORD_EMBEDDINGS_API = 'http://localhost:8888/'


def jsonify(obj):
    if '_id' in obj:
        del obj['_id']
    return flask_jsonify(obj)


from build_dict import Corpora
from synonyms import Synonyms

c = Corpora()
synonyms = Synonyms()
app = Flask(__name__)
db = MongoClient().ailas

def get_hints(word, n=10):
    """Return list of terms describing the word. """

    if not word:
        return []

    url = WORD_EMBEDDINGS_API + urllib.parse.quote(word)
    embeddings = [x[0] for x in requests.get(url).json()]

    sentences_hints = list(c.find_token_sentences(word, n=n))
    synonym_hints = synonyms.get_synonyms(word)

    hints = ([', '.join(embeddings[:2])] +
             sentences_hints[:3] +
             [', '.join(synonym_hints)] +
             [', '.join(embeddings[2:])] +
             ['Перша літера: "{}"'.format(word[0])] +
             sentences_hints[3:])

    return hints

def guess_by_hints(hints):

    candidates = Counter()
    for hint in hints:
        candidates.update(c.guess_candidates(hint))

    for h in hints:
        candidates[c.l.lemma(h)] = 0
    print (candidates)
    return [c for c, _ in candidates.most_common(30)]

def are_same_words(w1, w2):
    # TODO: w2 already lemmatize. this should be fixed in pick_word first
    return c.l.lemma(w1) == w2
    #return c.l.lemma(w1) == c.l.lemma(w2)

@app.route('/api/get_hint/<session_id>')
def api_get_hint(session_id, extra_msg=None):
    # TODO: get hint by request
    session = db.sessions.find_one({'id': session_id})
    current_hint_id = session['current_hint_id']
    try:
        hint = session['hints'][current_hint_id]
    except LookupError:
        return restart_session(session_id,
                               extra_msg='На жаль, використані всі можливі підказки. '
                                         'Моє слово було: {}'.format(session.get('word')))
    db.sessions.update({'id': session_id},
                       {'$inc': {'current_hint_id': 1}})

    if extra_msg:
        hint = extra_msg + '\n' + str(hint)

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
    callback = request.json.get('callback')
    return restart_session(session_id, callback)

def restart_session(session_id, callback=None, extra_msg=''):
    word = c.pick_word()
    hints = get_hints(word, n=50)
    session = {
        'id': session_id,
        'callback': callback,
        'active': True,
        'word': word,
        'hints': hints,
        'current_hint_id': 0,
    }
    db.sessions.update({'id': session_id},
                       {'$set': session},
                       upsert=True)
    return api_get_hint(session_id, extra_msg + '\n' + "GAME RESTARTED")



@app.route("/api/session/<session_id>/scores", methods=['GET'])
def api_session_scores(session_id):
    scores = []
    for s in db.scores.find({'sessionId': session_id}):
        scores.append({
            "user": s.get('user'),
            "score": s.get('score')
        })

    return jsonify({'scores': scores})

@app.route('/api/session/<session_id>/say', methods=['POST', 'PUT'])
def api_say(session_id):
    msg = request.json['txt'].lower()
    user = request.json['person']

    print(msg, '-------')

    db.messages.insert({
        "sessionId": session_id,
        "user": user,
        "msg": msg,
        "dt": datetime.datetime.now()
    })

    if msg.startswith("/guess "):
        msg = msg.partition(' ')[2]
        hint = guess_by_hints(msg.split())
    elif msg.startswith('/describe '):
        msg = msg.partition(' ')[2]
        hint = random.choice(get_hints(msg) or ['(dunno)'])
        return jsonify({"hint": hint})
    elif msg.startswith('/restart'):
        return restart_session(session_id)
    elif msg.startswith('/giveup'):
        session = db.sessions.find_one({'id': session_id})
        word = session['word']
        msg = 'Моє слово було {}'.format(word)
        return restart_session(session_id, extra_msg=msg)

    else:
        # Human's guess
        session = db.sessions.find_one({'id': session_id})
        if not session or not session.get('word'):
            return restart_session(session_id, extra_msg="Session started")

        if are_same_words(msg, session.get('word')):
            update_score(session_id, user, +50)
            return jsonify({"hint": "We've got THE WINNER! My word is {}".format(session['word']),
                            "win": True})
        else:
            update_score(session_id, user, -5)
            return api_get_hint(session_id)

def update_score(session_id, user, score_inc):
    db.scores.update({'sessionId': session_id, 'user': user},
                     {'$inc': {"score": score_inc}},
                     upsert=True)

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
