# -*- coding: utf-8 -*-
import itertools
from gensim.models import Word2Vec


class W2V(object):
    def __init__(self, model_filename='text_model_100'):
        self.model = Word2Vec.load(model_filename)

    def get_similair(self, word):
        q = self.model.most_similar(word)
        return q

    def filter_similarities(self, word, candidates):
        pairs = itertools.product(candidates, candidates)
        scores = dict([(i, 0) for i in candidates])
        for p1, p2 in pairs:
            if p1 != p2 and p1 != word and p2 != word:
                bad = self.model.doesnt_match([word, p1, p2])
                if bad == word:
                    scores[p1] -= 1
                    scores[p2] -= 1
                elif bad == p1:
                    scores[p1] -= 1
                    scores[p2] += 1
                elif bad == p2:
                    scores[p1] += 1
                    scores[p2] -= 1

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        good = [w for w, s in sorted_scores if s > 0]
        return good

    def get_last(self, word):
        similarities = self.get_similair(word)
        candidates = [s[0] for s in similarities]

        return candidates

    def get_similarity_bunch(self, word):
        total = set()
        stack = [word]
        while stack:
            current_word = stack.pop()
            candidates = self.get_last(current_word)
            filtered = self.filter_similarities(word, candidates)
            stack.extend(set(filtered).difference(total))
            total = total.union(set(filtered))

        return total


if __name__ == '__main__':
    w = W2V()
    for i in w.get_similarity_bunch('тато'.decode('utf-8')):
        print i
    print '****'
    for i in w.get_similair('тато'.decode('utf-8')):
        print i[0]