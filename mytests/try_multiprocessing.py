import os
from multiprocessing import Process


def f1(a):
    print(a*100)
    print('current process', os.getpid())
    for i in range(1, 10):
        print(i)
    print(a*100)


if __name__ == '__main__':
    print('Parent process', os.getpid())
    p1 = Process(target=f1, args=['-'])
    p1.start()
    p1.join() # 有没有这句话很重要.
    for i in range(100,200):
        print(i)
    print('child process end')
    '''
    output:
    
    Parent process 32200
    ----------------------------------------------------------------------------------------------------
    current process 32203
    1
    2
    3
    4
    5
    6
    7
    8
    9
    ----------------------------------------------------------------------------------------------------
    child process end
        
    '''
