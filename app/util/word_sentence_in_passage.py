import re


def word_sentence_in_passage(passage, word):
    result = re.split('[\.|\.\n]', passage)
    result = [item.strip() + '.' for item in result if item]
    result = [item for item in result if ' {} '.format(word) in item or ' {}.'.format(word) in item]
    return result