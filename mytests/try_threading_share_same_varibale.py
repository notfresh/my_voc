import threading, time

balance = 1000
lock = threading.Lock()


def deposit1(number):
    lock.acquire()
    try:
        global balance
        a = balance + number
        time.sleep(1)  # 主动让出cpu, 为什么这么做? 模拟CPU调度线程.
        balance = a
    finally:
        lock.release()


def deposit2(number):
    global balance
    a = balance + number
    balance = a


if __name__ == '__main__':
    t1 = threading.Thread(target=deposit1, name='first_deposit', args=[100])
    t2 = threading.Thread(target=deposit2, name='first_deposit', args=[200])
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print(balance)
