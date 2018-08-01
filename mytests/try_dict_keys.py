dict1 = {
    'a': 1,
    'b': 5,
    'c': 3
}
print(dict1.keys())
print(type(dict1.keys()))
print(type(list(dict1.keys())))

list1 = ['a', 'b']
import copy
dict1_copy = copy.copy(dict1)
for item in list(dict1_copy):
    if item in list1:
        dict1_copy.pop(item)
print(dict1_copy)

# try sorted
# sorted(dict1, key=lambda item: item[1])
dict2 = sorted(dict1.items(), key=lambda item: item[1])
# print(dict1)
print(dict2)
print(type(dict2))


