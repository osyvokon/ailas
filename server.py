from flask import Flask, request

from build_dict import Corpora

c = Corpora()

app = Flask(__name__)

def get_associations(word):
    """Return list of terms describing the word. """

    if not word:
        return []

    return c.find_token(word)



@app.route('/')
def hello_world():
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


