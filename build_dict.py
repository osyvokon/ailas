import re
import os
import glob
import gensim
import pickle
import numpy as np
from collections import defaultdict, Counter
from ukr_stemmer import UkrainianStemmer


MAX_CORPUS_SIZE = 400 * 1000 * 1000 # bytes
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

    def lemma(self, word, stem=True):
        word = word.lower().strip()
        if stem:
            stemmer = UkrainianStemmer(word)
            stemmed = stemmer.stem_word()
        else:
            stemmed = word
        return self.mappings.get(word, stemmed)


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

def split_sentences(text):
    return [s.strip() for s in re.split('[.!?\n]', text)]

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
        self.l = Lemmatizer()
        self.bigrams = gensim.models.Phrases()
        #self.phrases = []
        self.sentences = []

        os.makedirs('./cache', exist_ok=True)
        if os.path.exists('./cache/index'):
            self.index = pickle.load(open('./cache/index', 'rb'))
            self.sentences = pickle.load(open('./cache/sentences', 'rb'))
        else:
            loaded_size = 0
            files = glob.glob("./corpora/*/*")
            # np.random.seed(42)
            np.random.shuffle(files)
            for i, f in enumerate(files):
                if os.path.isfile(f):
                    loaded_size += os.path.getsize(f)
                    if loaded_size > MAX_CORPUS_SIZE:
                        break
                    print("loading", f, round(loaded_size / 1000 / 1000),  "mb")
                    self._add_document(f, find_phrases)
            pickle.dump(self.index, open("./cache/index", "wb"))
            pickle.dump(self.sentences, open("./cache/sentences", "wb"))

            print("Corpora loaded")
        print("{} sentences".format(len(self.sentences)))

    def _add_document(self, filename, find_phrases=False):
        stopwords = load_stopwords()
        with open(filename) as f:
            try:
                content = f.read()
            except UnicodeDecodeError:
                return

            sentences = split_sentences(content.lower())
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

    def pick_word(self):
        # take 20 random words and choose whatever has more sentences
        vocab = list(self.index.keys())
        # np.random.seed(42)
        cands = np.random.choice(vocab, size=200)
        word = sorted(cands, key=lambda w: len(self.index[w]))[-1]

        # TODO: find the original word in sentences. for now we're 
        # returning stemmed word
        return word

    def find_token_sentences(self, token, shorten=True, n=10):
        random_state = np.random.RandomState(42)
        t =  self.l.lemma(token)
        results = []
        indexes = self.index.get(t, [])
        stopwords = load_stopwords()
        random_state.shuffle(indexes)
        for sent_index in indexes:
            s = self.sentences[sent_index]
            print(s)
            s_tokens = tokenize(s)
            if len([x for x in s_tokens if x not in stopwords]) < 3:
                continue

            for x in s_tokens:
                if self.l.lemma(x) == t:
                    s = s.replace(x, "**AILAS**")

            if shorten:
                s = '\n'.join(re.findall(r"[\w ]*\*\*AILAS\*\*[\w ]*", s)).strip()

            results.append(s)

            if len(results) >= n:
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

    def guess_candidates(self, word):
        token = self.l.lemma(word)
        candidates = Counter()
        stopwords = load_stopwords()
        for sent_index in self.index.get(token, []):
            orig_sent = tokenize(self.sentences[sent_index])
            lemm_sent = [self.l.lemma(t) for t in orig_sent]
            i = lemm_sent.index(token)

            cs = [self.l.lemma(c, stem=False) for c in orig_sent[i-2:i] + orig_sent[i+1:i+3]]
            cs = [c for c in cs if c not in stopwords]
            candidates.update(cs)
        return candidates
    
