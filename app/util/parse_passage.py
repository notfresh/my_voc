import re
from collections import OrderedDict


def passage_to_word_list(str_passage):
    list1 = re.split(r'\s+', str_passage, flags=re.MULTILINE)
    # list1 = str_passage.split(' ')
    return list1


def strip_ext(str1, substr1):
    if substr1 in str1:
        return str1[:str1.index(substr1)]
    else:
        return str1


def filter_word_list(list_words):
    list_words = [item for item in list_words if item and len(item)>=3]
    # 过滤2， 把末尾的标点符号去掉， 比如逗号
    # TODO: 这些过滤应该整合起来,
    # TODO： 这些过滤只应该发生在头或者尾
    # 过滤3， 把末尾的标点符号去掉， 比如句号
    # TODO： 连字符，也应该被过滤掉
    list_words = [item.strip('-') for item in list_words]
    list_words = [item.strip('"') for item in list_words]
    list_words = [item.strip('(') for item in list_words]
    list_words = [item.strip(')') for item in list_words]
    list_words = [item.rstrip(';') for item in list_words]
    list_words = [item.rstrip(':') for item in list_words]
    list_words = [item.rstrip('.') for item in list_words]
    list_words = [item.rstrip(',') for item in list_words]
    list_words = [item.rstrip('，') for item in list_words]
    list_words = [item.rstrip('!') for item in list_words]
    list_words = [strip_ext(item, "'s") for item in list_words]
    # list_words = [item.strip(r'<br>') for item in list_words]
    list_words = [item.lower() for item in list_words]
    return list_words


def statistic(list_words):
    dict1 = OrderedDict()
    for item in list_words:
        if not dict1.get(item):
            dict1[item] = 1
        else:
            dict1[item] += 1
    return dict1


def filter_my_words(dict_word, list_my_words):
    key_list = list(dict_word)
    for item in key_list:
        if item in list_my_words:
            dict_word.pop(item)
        elif item.endswith('s'):
            if item.rstrip('s') in list_my_words:
                dict_word.pop(item)

    return dict_word

