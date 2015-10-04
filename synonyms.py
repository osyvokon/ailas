import re
from collections import OrderedDict

from build_dict import Lemmatizer


def _clean_syn(word):
    return re.sub(r'\([^)]*\)', '', word).strip()


def _process(word, syns):
    word = word.split('|')[0]
    syns = [_clean_syn(w) for w in syns.split('|')]
    syns = [i for i in syns if i]
    return word, syns


def parse_synonyms(filename='./data/th_uk_UA.dat.txt'):
    lemmatizer = Lemmatizer()
    synonyms = OrderedDict()
    with open(filename) as f:
        word = None
        for line in f:
            if word is None and line is not None and not line.startswith('|'):
                word = line
            elif word is not None:
                word, syns = _process(word, line)
                # clean synonyms from too similar words
                lemma_word = lemmatizer.lemma(word)
                syns_filtered = [s for s in syns if lemma_word != lemmatizer.lemma(s)]
                if syns_filtered:
                    synonyms[word] = syns_filtered

                word = None

    return synonyms


class Synonyms:
    def __init__(self, filename='./data/th_uk_UA.dat.txt'):
        self.lemmatizer = Lemmatizer()
        self.synonyms = parse_synonyms(filename)
        self.lemmed_synonyms = {}
        for w, s in self.synonyms.items():
            self.lemmed_synonyms[self.lemmatizer.lemma(w)] = s

    def get_synonyms(self, word):
        if word in self.synonyms:
            return self.synonyms[word]
        return self.lemmed_synonyms.get(self.lemmatizer.lemma(word), [])


if __name__ == '__main__':
    s = Synonyms()
    print(s.get_synonyms('огида'))
    # for k,v in parse_synonyms().items():
    #     print(k)
    #     print('-')
    #     for s in v:
    #         print(s)
    #     print('****')