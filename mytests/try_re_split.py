import re

a = ' to says the least. his his "'
a_list = re.split('\s+', a)
a_list = ['his', 'was', 'surprisingly', 'straight', 'up']
list_words = [item.strip("\'s") for item in a_list]
for item in a_list:
    if item == 'his':
        print(1)
        print(item.rstrip("'s"))
print(list_words)

a = "his's"
print("'s" in a)
print(a.index("'s"))
print(a[:a.index("'s")])


