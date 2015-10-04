# -*- coding: utf-8 -*-
import multiprocessing
import gensim
from gensim.models import Word2Vec, Phrases
from nltk.data import load
import nltk
import string
import re
import os

regex = re.compile('[%s]' % re.escape(string.punctuation + u'—' + u'-' + u'…' + u'«' + u'»'))
# table = string.maketrans('', '')
punctuation_tokenizer = load('tokenizers/punkt/english.pickle')


def sentance_extractor(filename):
    with open(filename, 'r', encoding='utf-8', errors="surrogateescape") as f:
        buffer = []
        for line in f:
            # line = line.decode('utf-8', 'ignore')
            dot_pos = line.find('.')
            if dot_pos != -1:
                buffer.append(line[:dot_pos+1].strip())
                for s in punctuation_tokenizer.tokenize(' '.join(buffer)):
                    s = regex.sub('', s.strip()).lower()
                    s = nltk.word_tokenize(s)
                    if s:
                        yield s
                buffer = [line[dot_pos+1:].strip()]
            else:
                buffer.append(line.strip())


def process_corpus(folder_name):
    for dirName, subdirList, fileList in os.walk(folder_name):
        print(dirName)
        if not dirName.startswith('.'):
            for i, filename in enumerate(fileList):
                if (i+1) % 10 == 0:
                    print((i+1) / 10)
                for s in sentance_extractor(os.path.join(dirName, filename)):
                    yield s


def w2v():
    # data = [i for i in sentance_extractor('/Users/valeriyischenko/local/projects/lingua_hack/Text/Detective/99')]
    # data = [i for i in process_corpus('/Users/valeriyischenko/local/projects/lingua_hack/Text')]
    # print 'Get all data'
    model = Word2Vec(size=200, window=5, min_count=5, workers=multiprocessing.cpu_count())
    # model = Word2Vec(sentences=data, size=200, window=5, min_count=5, workers=multiprocessing.cpu_count())
    model.build_vocab(process_corpus('Text'))
    model.train(process_corpus('Text'))

    model.init_sims(replace=True)
    model.save('../wiki/text_model_p3')


def phrases():
    p = Phrases(sentences=process_corpus('/Users/valeriyischenko/local/projects/lingua_hack/Text'))
    p.save('../wiki/text_phrase_model_p3')


if __name__ == '__main__':
    w2v()
    # phrases()