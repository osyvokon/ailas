import re
import os
import glob
import gensim
import pickle
import numpy as np
from collections import defaultdict
from ukr_stemmer import UkrainianStemmer


MAX_CORPUS_SIZE = 500 * 1000 * 1000 # bytes
MAX_SENTENCES_PER_WORD = 100

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
    assert l.lemma('АДАма') == 'адам'
    assert l.lemma('яблуко') == 'яблуко'


def load_stopwords():
    if not hasattr(load_stopwords, 'cache'):
        with open('./data/stopwords.txt') as f:
            load_stopwords.cache = set(f.read().split('\n'))
    return load_stopwords.cache

def test_stopwords():
    assert 'або' in load_stopwords()
    assert 'червоний' not in load_stopwords()

def split_sentences(s):
    return [s.strip() for s in re.split('[.!?\n]', s)]

def test_split_sentences():
    assert split_sentences("Hello, world! How. Are? You") == [
        "Hello, world",
        "How",
        "Are",
        "You"]

def tokenize(s):
    return re.findall("\w+", s)


def test_tokenize_simple():
    assert tokenize('привіт, світе!') == ['привіт', 'світе']


class Corpora:
    def __init__(self, find_phrases=False):
        self.index = defaultdict(list)     # token => sentence indexes
        l = self.l = Lemmatizer()
        self.bigrams = gensim.models.Phrases()
        #self.phrases = []
        self.sentences = []

        os.makedirs('./cache', exist_ok=True)
        if os.path.exists('./cache/index'):
            self.index = pickle.load(open('./cache/index', 'rb'))
            self.sentences = pickle.load(open('./cache/sentences', 'rb'))
        else:
            loaded_size = 0
            for i, f in enumerate(glob.glob("./corpora/Text/Fiction/*")):
                if os.path.isfile(f):
                    loaded_size += os.path.getsize(f)
                    if loaded_size > MAX_CORPUS_SIZE:
                        break
                    print("loading", f)
                    self._add_document(f, find_phrases)
            pickle.dump(self.index, open("./cache/index", "wb"))
            pickle.dump(self.sentences, open("./cache/sentences", "wb"))
            print("Corpora loaded")

    def _add_document(self, filename, find_phrases=False):
        stopwords = load_stopwords()
        with open(filename) as f:
            sentences = split_sentences(f.read().lower())
            sentences_tokenized = []
            for sentence_index, s in enumerate(sentences, len(self.sentences)):
                tokens = [self.l.lemma(t) for t in tokenize(s) if t not in stopwords]
                for t in tokens:
                    if len(self.index[t]) < MAX_SENTENCES_PER_WORD:
                        self.index[t].append(sentence_index)
                if find_phrases:
                    sentences_tokenized.append(tokens)

        #bigrams = gensim.models.Phrases(sentences_tokenized)
        #phrases = [s.decode() for s in bigrams.vocab.keys()
                        #if b'_' in s]
        #self.phrases += phrases
        self.sentences += sentences
        if find_phrases:
            self.bigrams.add_vocab(sentences_tokenized)

        #print("{}: {} sentences, {} phrases".format(filename, len(sentences), len(phrases)))

    @property
    def phrases(self):
        phrases = [s.decode() for s, c in self.bigrams.vocab.items()
                   if c > 1 and b'_' in s]
        print(list(self.bigrams.vocab.items())[:100])
        return phrases

    def find_token_sentences(self, token, shorten=True, n=10):
        results = []
        indexes = self.index.get(self.l.lemma(token), [])
        np.random.shuffle(indexes)
        for sent_index in indexes:
            s = self.sentences[sent_index]
            print(s)
            for t in tokenize(s):
                if self.l.lemma(t) == token:
                    s = s.replace(t, "**ALIAS**")

            if shorten:
                s = '\n'.join(re.findall(r"[\w ]*\*\*ALIAS\*\*[\w ]*", s)).strip()

            results.append(s)

            if len(s) >= n:
                break

        return results

    def find_token_pharses(self, token):
        result = list()
        t = self.l.lemma(token)
        v = self.bigrams.vocab

        for sent_index in self.index.get(t, []):
            orig_sent = self.sentences[sent_index]

            result.append((0, orig_sent))
            continue

            lemm_sent = [self.l.lemma(t) for t in tokenize(orig_sent)]
            phrases = [x for x in self.bigrams[tokenize(orig_sent)]
                       if '_' in x and t in x]
            if not phrases:
                continue

            l1, l2 = phrases[0].split("_")
            start = end = 0
            for i, t in enumerate(tokenize(orig_sent)):
                lemm_t = self.l.lemma(t)
                if lemm_t == l1:
                    start = i
                elif lemm_t == l2:
                    end = i
                else:
                    pass

            excerpt = ' '.join(orig_sent[start:end])
            result.append((v[phrases[0]], excerpt))

        return [x[1] for x in sorted(result, reverse=True)]

