in_stack_priority = {
    '#': 0,
    '+': 3,
    '-': 3,
    '*': 5,
    '/': 5,
    '(': 1,
    ')': 6,
}
coming_priority = {
    '#': 0,
    '+': 2,
    '-': 2,
    '*': 4,
    '/': 4,
    '(': 6,
    ')': 1,
}


def f1(a):
    # set1: 设置符号栈, 设置输出队列
    a.append('#')
    stack = ['#']
    output_list = []
    for coming in a:
        # 判断您是否是数字, 是数字, 直接进入输出队列
        if coming.isdigit():
            output_list.append(coming)
        else:
            while True:
                if in_stack_priority.get(stack[-1]) > coming_priority.get(coming):
                    output_list.append(stack.pop())
                elif in_stack_priority.get(stack[-1]) < coming_priority.get(coming):
                    stack.append(coming)
                    break
                else:
                    stack.pop()
                    break
    return output_list


str1 = list('1+2+3')  # 目标 12+3+, 汉字注释不带空格是绝对的.
str2 = list('1+2+3+4')  # 目标 12+3+4+,
str3 = list('1+2+3+4-5')  # 目标 12+3+4+5-,
str4 = list('1*2+3')  # 目标 12*3+,
str5 = list('1+2*3')  # 目标 123*+,
str6 = list('1+2*3+4')  # 目标 123*+4+,
str7 = list('1+2*3+4+5')  # 目标 123*+4+5+,
str8 = list('1+2*3+4+5*6')  # 目标 123*+4+56*+,
str9 = list('1+2*3+4+5*6*7')  # 目标 123*+4+56*7*+,
str10 = list('1+2*3+4+5*6*(7+8*9)+9')  # 目标 123*+4+56*789*+*+9+
str11 = list('1+(2+3)*4')  # 123+4*+
print(f1(str1))
print(f1(str2))
print(f1(str3))
print(f1(str4))
print(f1(str5))
print(f1(str6))
print(f1(str7))
print(f1(str8))
print(f1(str9))
print(f1(str10))
print(f1(str11))
