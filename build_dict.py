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
            Lemmatizer.mappings = d
            # print(d)

    def lemma(self, word):
        word = word.lower().strip()
        stemmer = UkrainianStemmer(word)
        if word in self.mappings:
            default_word = word
        else:
            default_word = stemmer.stem_word()
        return self.mappings.get(word, default_word)


def test_lemmatizer():
    l = Lemmatizer()
    assert l.lemma('адама') == 'адам'
