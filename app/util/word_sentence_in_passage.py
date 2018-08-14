import re


def word_sentence_in_passage(passage, word):
    result = re.split('[\.|\.\n]', passage)
    result = [item.strip() + '.' for item in result if item]
    word = ' {}'.format(word)
    result = [item for item in result if word in item or word+'.' in item]
    return result