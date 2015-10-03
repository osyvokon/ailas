from flask import Flask, request, jsonify as flask_jsonify
from pymongo import MongoClient


def jsonify(obj):
    if '_id' in obj:
        del obj['_id']
    return flask_jsonify(obj)


from build_dict import Corpora

#c = Corpora()
app = Flask(__name__)
db = MongoClient().ailas

def get_associations(word):
    """Return list of terms describing the word. """

    if not word:
        return []

    return c.find_token_pharses(word)


@app.route('/api/session', methods=['GET'])
def api_session_list():
    return jsonify({
        "sessions": list(db.sessions.find({'active': True}, fields={'_id': 0}))
    })

@app.route('/api/session', methods=['POST', 'PUT'])
def api_session_start():
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
    msg = request.json['message']
    user = request.json['user']
    db.messages.insert({
        "sessionId": session_id,
        "user": user,
        "msg": msg,
        "dt": datetime.datetime.now()
    })

    return jsonify({"ok": True})

@app.route('/api/session/<session_id>', methods=['DELETE'])
def api_session_delete(session_id):
    db.sessions.update({"id": session_id}, {'$set': {'active': False}})
    return jsonify({"ok": True})


@app.route('/')
def form():
    query = request.args.get('query')
    associations = get_associations(query)

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


