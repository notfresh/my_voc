def feb(max):
    n, a, b = 1, 0, 1
    while n <= max:
        yield a
        a, b = b, a + b
        n += 1


print(list(feb(1)))