# -*- coding:utf-8 -*-
import os


def read_current_dir_files(dir_path):
    """
    把当前目录下所有的文件读进来, 包括文件和文件对象
    :return: 返回一个文件对象列表
    """
    file_list = []
    for thefile in os.listdir(dir_path):
        # file_path = os.path.join(dir_path, thefile)
        file_list.append(thefile)
    return file_list


def update_a_file_name(file, file_new_name):
    os.rename(file, file_new_name)


def new_file_name(name):
    a = '2019考研英语朱伟恋练有词考研词汇（恋恋有词） - 1.01.2019年朱伟练练有词导学开班仪式★微信公众号：zqky666【+资源(Av20509547,P1).Flv'
    b = '2019考研英语朱伟恋练有词考研词汇（恋恋有词） - '
    if b in name:
        new_name = name.replace(b, '')
        return new_name
    return name


if __name__ == '__main__':
    current_dir = os.path.dirname(__file__)
    file_list = read_current_dir_files(current_dir)
    for item in file_list:
        new_name = new_file_name(item)
        update_a_file_name(item, new_name)





