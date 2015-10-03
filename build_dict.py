import re
import glob
import gensim
from collections import defaultdict
from ukr_stemmer import UkrainianStemmer

class Lemmatizer:
    mappings = None

    def __init__(self):
        if Lemmatizer.mappings is None:
            d = {}
            with open("./data/lemmatization-uk.txt") as f:
                for line in f:
                    main, _, form = line.lower().strip().partition('\t')
                    d[form] = main
                    d[main] = main
            Lemmatizer.mappings = d
            # print(d)

    def lemma(self, word):
        word = word.lower().strip()
        stemmer = UkrainianStemmer(word)
        return self.mappings.get(word, stemmer.stem_word())


def test_lemmatizer():
    l = Lemmatizer()
    assert l.lemma('адама') == 'адам'
    assert l.lemma('яблуко') == 'яблуко'


def load_stopwords():
    if not hasattr(load_stopwords, 'cache'):
        with open('./data/stopwords.txt') as f:
            load_stopwords.cache = set(f.read().split('\n'))
    return load_stopwords.cache

def test_stopwords():
    assert 'або' in load_stopwords()
    assert 'hello' not in load_stopwords()

def split_sentences(s):
    return re.split('[.!?]\n', s)

def tokenize(s):
    return re.findall("\w+", s)


def test_tokenize_simple():
    assert tokenize('привіт, світе!') == ['привіт', 'світе']


class Corpora:
    def __init__(self):
        self.index = defaultdict(list)     # token => sentence indexes
        l = self.l = Lemmatizer()
        self.bigrams = gensim.models.Phrases()
        self.phrases = []
        self.sentences = []

        for f in glob.glob("./corpora/*.txt"):
            self._add_document(f)

    def _add_document(self, filename):
        stopwords = load_stopwords()
        with open(filename) as f:
            sentences = split_sentences(f.read())
            sentences_tokenized = []
            for sentence_index, s in enumerate(sentences):
                tokens = [self.l.lemma(t) for t in tokenize(s) if t not in stopwords]
                for t in tokens:
                    self.index[t].append(sentence_index)
                sentences_tokenized.append(tokens)

        bigrams = gensim.models.Phrases(sentences_tokenized)
        phrases = [s.decode() for s in bigrams.vocab.keys()
                        if b'_' in s]
        self.phrases += phrases
        self.sentences += sentences

        print("{}: {} phrases".format(filename, len(phrases)))

    def find_token_sentences(self, token):
        for sent_index in self.index.get(self.l.lemma(token), []):
            s = self.sentences[sent_index]
            yield ' '.join(s)

    def find_token_pharses(self, token):
        result = set()
        t = self.l.lemma(token)
        for p in self.phrases:
            if t in p.split('_'):
                result.add(p)

        return result


def test_find_token():
    c = Corpora()
    # TODO: split by sentences
    assert c.find_token('ворон')[0] == 'вершечку акації чорного ворона Той сидів'


