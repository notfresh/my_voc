import re
from collections import OrderedDict


def passage_to_word_list(str_passage):
    str_passage = str_passage.replace('’', '\'')
    str_passage = str_passage.replace('”', '"')
    str_passage = str_passage.replace('“', '"')
    str_passage = str_passage.replace('，', ',')
    # in case of the [A] and the following word attached, so i add one more space.
    str_passage = str_passage.replace('[A]', '[A] ')
    str_passage = str_passage.replace('[B]', '[B] ')
    str_passage = str_passage.replace('[C]', '[C] ')
    str_passage = str_passage.replace('[D]', '[D] ')
    list1 = re.split(r'[\s+|/|:|,]', str_passage, flags=re.MULTILINE)
    # list1 = str_passage.split(' ')
    return list1


def strip_ext(str1, substr1):
    if substr1 in str1:
        return str1[:str1.index(substr1)]
    else:
        return str1


def digit_in_str(str1):
    regex = r'[1234567890]'
    if re.search(regex, str1):
        return True
    else:
        return False


def judge_pure_english(keyword):
    return all(ord(c) < 128 for c in keyword)


def filter_word_list(list_words):
    list_words = [item for item in list_words if item and len(item)>=3 and not digit_in_str(item)]
    list_words = [item for item in list_words if judge_pure_english(item)] # only english will be left.
    # 过滤2， 把末尾的标点符号去掉， 比如逗号
    # TODO: 这些过滤应该整合起来,
    # TODO： 这些过滤只应该发生在头或者尾
    # 过滤3， 把末尾的标点符号去掉， 比如句号
    # TODO： 连字符，也应该被过滤掉
    list_words = [item.strip('"') for item in list_words]
    list_words = [item.strip('\'') for item in list_words]
    list_words = [item.strip('.') for item in list_words]

    list_words = [item.strip('-') for item in list_words]
    list_words = [item.strip('(') for item in list_words]
    list_words = [item.strip(')') for item in list_words]
    list_words = [item.rstrip(';') for item in list_words]
    list_words = [item.rstrip('?') for item in list_words]
    list_words = [item.rstrip(':') for item in list_words]
    list_words = [item.rstrip(',') for item in list_words]
    list_words = [item.rstrip('!') for item in list_words]

    # strip again !
    list_words = [item.strip('"') for item in list_words]
    list_words = [item.strip('\'') for item in list_words]
    list_words = [item.strip('.') for item in list_words]

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
        elif item.startswith('a.') or item.startswith('b.') or item.startswith('c.') or item.startswith('d.'):
            dict_word.pop(item)
        elif item.endswith('s'):
            if item.rstrip('s') in list_my_words:
                dict_word.pop(item)
        elif item.endswith('es'):
            if item.rstrip('es') in list_my_words:
                dict_word.pop(item)
        elif item.endswith('ed'):
            if item.rstrip('ed') in list_my_words:
                dict_word.pop(item)
            elif item.rstrip('d') in list_my_words:
                dict_word.pop(item)
        elif item.endswith('ing'):
            if item.rstrip('ing') in list_my_words:
                dict_word.pop(item)
            elif len(item) >= 5 and item[-4] == item[-5]:
                if item[:-4] in list_my_words:
                    dict_word.pop(item)
            elif item[:-3] + 'e' in list_my_words:
                dict_word.pop(item)
        elif item.endswith('ly'):
            if item.rstrip('ly') in list_my_words:
                dict_word.pop(item)

    return dict_word

