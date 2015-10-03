import re

class Lemmatizer:
    mappings = None

    def __init__(self):
        if Lemmatizer.mappings is None:
            d = {}
            with open("./data/lemmatization-uk.txt") as f:
                for line in f:
                    main, _, form = line.lower().strip().partition('\t')
                    d[form] = main
            Lemmatizer.mappings = d

    def lemma(self, word):
        word = word.lower().strip()
        return self.mappings.get(word, word)


def test_lemmatizer():
    l = Lemmatizer()
    assert l.lemma('адама') == 'адам'



def tokenize(s):
    return re.findall("\w+", s)


def test_tokenize_simple():
    assert tokenize('привіт, світе!') == ['привіт', 'світе']


class Corpora:
    def __init__(self):
        with open("./corpora/book1.txt") as f:
            self.doc = tokenize(f.read())

        self.l = Lemmatizer()
        self.lemmas = map(self.l.lemma, self.doc)

    def find_token(self, token, context=3):
        phrases = []
        t = self.l.lemma(token)
        i = -1
        while True:
            try:
                i = self.doc.index(t, i+1)
                phrase = ' '.join(self.doc[i-context : i+context])
                phrases.append(phrase)
            except ValueError:
                return phrases

def test_find_token():
    c = Corpora()
    # TODO: split by sentences
    assert c.find_token('ворон')[0] == 'вершечку акації чорного ворона Той сидів'


