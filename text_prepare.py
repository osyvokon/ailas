#!/usr/bin/env python3.5

import re
import build_dict


def text_prepare(text):
    text = text.lower()
    pattern = r"[а-яА-ЯґҐЇїіІєЄ'’]+"
    pattern_exp = re.compile(pattern, re.MULTILINE & re.LOCALE)
    return pattern_exp.findall(text)

def modify_text(text, word, rpl='BANANA'):
    lemmtizer = build_dict.Lemmatizer()

    def replace(word):
        nonlocal text, rpl
        text = re.sub(word, rpl, text)

    for current_word in text_prepare(text):
        lemma = lemmtizer.lemma(current_word)
        if lemma == word:
            replace(current_word)

    return text

if __name__ == '__main__':
    text = 'Яблуко було дуже смачне. Я люблю яблука.'
    print(modify_text(text=text,
                      word='яблуко'))
