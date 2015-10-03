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
            print(d)

    def lemma(self, word):
        word = word.lower().strip()
        return self.mappings.get(word, word)


def test_lemmatizer():
    l = Lemmatizer()
    assert l.lemma('адама') == 'адам'
