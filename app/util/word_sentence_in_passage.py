import re


def next_char(str1, substr1):
    index = str1.index(substr1) + len(substr1)
    try:
        next_char = str1[index]
    except Exception:
        return '#'
    return next_char


def before_char(str1, substr1):
    index = str1.index(substr1)
    if index == 0:
        return '#'
    before = str1[index-1]
    return before


def word_sentence_in_passage(passage, word):
    sentences = re.split('[\.[^\n]\s|(\.\n)|(\?)]', passage)
    sentences = [item.strip() + '.' for item in sentences if item]
    # # 这个单词在这个句子中，但是这个单词后面应该跟的是一个标点符号而不是字母，从而排除了这个单词作为另外一个单词一部分的可能。
    result = [item for item in sentences if word in item.lower() and not next_char(item.lower(), word).isalpha()\
              and not before_char(item.lower(), word).isalpha()]
    return result
