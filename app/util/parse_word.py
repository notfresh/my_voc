import pprint
from collections import OrderedDict

from app import db
from app.exceptions import DataError, error_dict
from app.models import Word

a = '''  
w: study
itp: V-T/V-I | If you study, you spend time learning about a particular subject or subjects.
eap: a relaxed and happy atmosphere that will allow you to study to your full potential.
eap: He studied History and Economics.
itp: N-UNCOUNT | Study is the activity of studying. | 学习
eap: the use of maps and visual evidence in the study of local history.
itp: N-COUNT | A study of a subject is a piece of research on it. 研究
eap: Recent studies suggest that as many as 5 in 1,000 new mothers are likely to have this problem.
itp: N-PLURAL | You can refer to educational subjects or courses that contain several elements as studies of a particular kind.| 学科
'''

'''
期望把它变成
{
    'w': 'study',
    'itp': [
        {
            'itp_str': 'If you study, you spend time learning about a particular subject or subjects.',
            'itp_type': 'V-T/V-I',
            'eap': [
                'a relaxed and happy atmosphere that will allow you to study to your full potential.',
                'He studied History and Economics.'
            ]
        },
        {
            'itp_str': 'Study is the activity of studying. | 学习',
            'itp_type': 'N-UNCOUNT',
            'eap': [
                'Recent studies suggest that as many as 5 in 1,000 new mothers are likely to have this problem.'
            ]
        },
        {
            'itp_str': 'You can refer to educational subjects or courses that contain several elements as studies of a particular kind.| 学科',
            'itp_type': 'N-PLURAL'
        },
    ]
}
'''


def parse_word(word_str):
    lines = [item for item in word_str.replace('\r', '').split('\n') if item.strip()]
    current_word = OrderedDict()
    itp_list = []
    current_itp = OrderedDict()

    for item in lines:
        item = item.strip()
        if item.startswith('w:'):
            current_word['w'] = item.replace('w:', '').strip()
        elif item.startswith('itp:'):
            if current_itp:
                itp_list.append(current_itp)
                current_itp = {}
            if '|' not in item: # 一行内以短竖线分割. 如果没有 | 划分, 说明有错.
                raise DataError('INTERPRETATION_FAULT', error_dict['INTERPRETATION_FAULT'])
            itp_list1 = item.replace('itp:', '').split('|')  # 一行内以短竖线分割.
            current_itp['itp_type'] = itp_list1[0]
            itp_list1.pop(0)
            current_itp['itp_str'] = ';'.join(itp_list1)
        elif item.startswith('eap:'):
            current_itp['eap'] = current_itp.get('eap') or []
            current_itp['eap'].append(item.replace('eap:', ''))
    if current_itp:
        itp_list.append(current_itp)
    if itp_list:
        current_word['itp'] = itp_list
    return current_word


def word_to_str(word):
    pass
    str_word = ''
    line_feed = '\r\n'
    str_word += 'w: ' + word.word + line_feed
    for ipt_item in word.interpretations:
        str_word += 'itp: ' + ipt_item.type + '| ' + ipt_item.interpretation + line_feed
        for eap_item in ipt_item.examples:
            str_word += 'eap: ' + eap_item.example + line_feed
    return str_word


if __name__ == '__main__':
    word = db.session.query(Word).filter(Word.word == 'study').first()
    dict_word = word_to_str(word)
    print(dict_word)
