class ValidationError():
    pass


class DataError(Exception):

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg


error_dict = {
    10000: '数据重复'
}