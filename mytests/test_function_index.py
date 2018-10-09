

str1 = 'a apple applepie'
substr1 = 'apple'
index = str1.index(substr1) + len(substr1)
next_char = str1[index]
print(index)
print(next_char)
print(next_char != ' ')
print(next_char.isalpha())


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
    next_char = str1[index-1]
    return next_char


print('*'*10)
print(before_char(str1, 'a'))
