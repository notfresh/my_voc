import multiprocessing
bind = '127.0.0.1:9010'
worker = multiprocessing.cpu_count()*2+1
