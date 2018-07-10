class ABC:

    list1 = [1, 2, 3]

    def __init__(self, method1):
        self.method1 = method1


def pop_list(list1):
    list1.pop()


if __name__ == '__main__':
    a = ABC(pop_list)
    a.method1(a.list1)
    print(a.list1)