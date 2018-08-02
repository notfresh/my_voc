import re


# re.search方法是什么?
def test_what_is_re_search():
    str1 = r"hello. hell1231o. world "
    regex = r"[A]"
    result = re.search(regex, str1)
    print(type(result))
    print(result)
    print(result.group())


if __name__ == '__main__':
    test_what_is_re_search()