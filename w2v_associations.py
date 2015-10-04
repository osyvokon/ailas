from gensim.models import Word2Vec


class W2V:
    def __init__(self):
        self.model = Word2Vec.load('text_model_100')

    def get_similair(self, word):
        q = self.model.most_similar(word)
        return q
