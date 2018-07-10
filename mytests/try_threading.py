import threading
import os


def f1():
    print('f1', 'current threading', threading.current_thread().name)
    for i in range(1, 10):
        print(i)


if __name__ == '__main__':
    thread1 = threading.Thread(target=f1, name='thread1')
    thread1.start()
    thread1.join()
    for i in range(100, 110):
        print(i)

'''
f1 current threading thread1
1
2
3
4
5
6
7
8
9
100
101
102
103
104
105
106
107
108
109

'''