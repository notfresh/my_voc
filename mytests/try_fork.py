import os

print('process start')
pid = os.fork()  # 这个代码以后的代码通通会执行2次.
print('xx:', pid)
if pid != 0:
    print('i am parent process', pid)
else:
    print('i am child process', pid, 'my parent process is', os.getppid())

print(1, 2, 3, 4, 5, 6)

'''
output:
----------------------------------------------------------------------------------------
process start
xx: 25233
i am parent process 25233
1 2 3 4 5 6
xx: 0
i am child process 0 my parent process is 25232
1 2 3 4 5 6
----------------------------------------------------------------------------------------

'''