from gensim.models import Word2Vec


class W2V:
    def __init__(self, model_file):
        self.model = Word2Vec.load('text_model')

    def get_similair(self, word):
        wu = word.decode('utf-8')
        q = self.model.most_similar(wu)
        # print '*'*5
        # for i in q:
        #     print i[0], i[1]
        # print '-'*20
        return q
