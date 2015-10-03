import re
from collections import defaultdict

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



def split_sentences(s):
    return s.split('.')

def tokenize(s):
    return re.findall("\w+", s)


def test_tokenize_simple():
    assert tokenize('привіт, світе!') == ['привіт', 'світе']


class Corpora:
    def __init__(self):
        self.index = defaultdict(list)     # token => sentence indexes
        l = self.l = Lemmatizer()

        with open("./corpora/book1.txt") as f:
            self.sentences = list(map(tokenize, split_sentences(f.read())))
            for sentence_index, s in enumerate(self.sentences):
                for t in s:
                    self.index[l.lemma(t)].append(sentence_index)

    def find_token(self, token, context=3):
        for sent_index in self.index.get(self.l.lemma(token), []):
            s = self.sentences[sent_index]
            yield ' '.join(s)


def test_find_token():
    c = Corpora()
    # TODO: split by sentences
    assert c.find_token('ворон')[0] == 'вершечку акації чорного ворона Той сидів'


