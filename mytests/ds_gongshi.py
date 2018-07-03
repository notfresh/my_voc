def expect(p):
    parenthesis = {
        '(': ')',
        '[': ']',
    }
    p_want = parenthesis.get(p)
    return p_want


def is_left(p):
    list1 = ['(', '[']
    if p in list1:
        return True
    else:
        return False


strs = '[([][])]'
# strs = '[()]'

a = list(strs)


def check_parenthesis_list(a):
    if isinstance(a, list):
        a = list(a)
    flag = True
    stack = []
    p_want = ''
    # case1: 先进来的是 '('. 第二个进来的是 ')', OK
    # question1: 如何判断一个符号可以入栈? 1. 如果是左, 可入. 2. 如果是右, 检查是否符合栈顶.
    # case2: 进来'(', 怎么处理? ans: step1: 检查左右属性; step2: 是左, 压栈. step:2.1:是右, 判断是否符合期待. 符合, 栈顶元素退栈.下一个, 然后修改expect的值
    #       不符合, 结束.
    # 依次读取每个元素, 并压栈, 设置期待值, 比如 "(" 的期待值是 ")", "["的期待值是"]", 没有左括号, 获取右括号, 直接报错.
    for i in range(0, len(a)):
        p = a[i]
        if is_left(p):
            stack.append(p)
            expected = expect(p)
        else:
            if p == expected:
                stack.pop()
                if stack:  # 如果栈没空, 设置期待值, 否则
                    expected = expect(stack[-1])
            else:
                flag = False
                break
    # case3: 遍历结束, 栈不为空. 那么符号列有问题.
    if stack:
        flag = False
    return flag


print(check_parenthesis_list(a))
