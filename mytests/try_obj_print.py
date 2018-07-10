class Printer:

    def __repr__(self):
        dict_attr = self.__dict__
        dict_attr_public = {item[0]: item[1] for item in dict_attr.items() if not item[0].startswith('_')}
        return str(dict_attr_public)


class A:
    a = 'abc'
    b = 'xyz'

    def __str__(self):
        dict_attr = self.__class__.__dict__
        dict_attr_public = {item[0]: item[1] for item in dict_attr.items() if not item[0].startswith('_')} #
        return str(dict_attr_public)


if __name__ == '__main__':
    a = A()
    print('-'*100)
    print('-'*100)
    print(a)
    '''
    output:
    
    '''
