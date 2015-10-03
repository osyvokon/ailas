#!/usr/bin/env python3.5

import re


def text_prepare(text):
    text = text.lower()
    pattern = r"[а-яА-ЯґҐЇїіІєЄ'’]+"
    pattern_exp = re.compile(pattern, re.MULTILINE & re.LOCALE)
    return pattern_exp.findall(text)

def modify_text(text):
    def replace(word, rpl):
        nonlocal text
        re.sub(word, rpl, text)
