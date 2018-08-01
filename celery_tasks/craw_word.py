# coding:utf-8
import os
import re

import xmltodict
from scrapy import Spider
from scrapy.crawler import CrawlerProcess

from app.exceptions import DataError, error_dict
from app.models import Word, WordIPEAP, WordInterpretation
from celery_tasks.models import Session


def write_obj_to_file(obj):
    import json
    filename = 'output.json'
    f = open(filename, 'a')
    f.write(json.dumps(obj) + '\n')
    f.close()
    print('*'*100, '\n', 'output finished', os.getcwd());


def update_word(dict_word):
    session = Session()
    word_obj = session.query(Word).filter(Word.word == dict_word['w']).first()
    if not word_obj:
        raise DataError('WORD_NOT_FOUND', error_dict['WORD_NOT_FOUND'])
    session.query(WordIPEAP).filter(WordIPEAP.word_id == word_obj.id).delete()
    session.query(WordInterpretation).filter(WordInterpretation.word_id == word_obj.id).delete()
    word_obj.phonetics = dict_word.get('ph')
    word_obj.note = dict_word.get('n')
    for itp_item in dict_word.get('itp') or []:
        itp_obj = WordInterpretation.create_word_interpretation(word_obj, itp_item['itp_type'], itp_item['itp_str'], session)
        for eap_item in itp_item.get('eap') or []:
            WordIPEAP.create_word_ipeap(itp_obj, eap_item, session)
    session.add(word_obj)
    session.commit()
    session.close()


# define a spider
class YoudaoDictSpider(Spider):
    name = 'shiyanlou_spider1'

    def __init__(self, word=None, word_method=None):
        """
        :param word: 要爬的单词的列表
        :param dict_method: 对处理的对象的办法.
        """
        super().__init__()
        self.word = word
        url = 'http://dict.youdao.com/w/eng/{}/'
        self.start_urls = [url.format(word)]
        self.word_method = word_method

    def parse(self, response):
        word = self.word
        output_item = {'w': word, 'ph': '', 'itp': []}
        trans = response.css('div#authTrans div#collinsResult')
        word_phonetics = trans.css('em[class="additional spell phonetic"]::text').extract_first()
        if word_phonetics:
            output_item['ph'] = word_phonetics
        trans_list = trans.css('ul.ol>li')
        for item in trans_list:
            word_str = item.css('div.collinsMajorTrans p').extract_first()
            trans_item = {}
            if not word_str:
                continue
            word_str_clean = re.sub('\s{2,}', '', word_str)
            if '<b>' in word_str_clean:
                word_str_clean = word_str_clean.replace('<b>', '').replace('</b>', '')
            word_dict = xmltodict.parse(word_str_clean)
            span_node = word_dict.get('p').get('span')
            try:
                if type(span_node) == list:
                    word_type = span_node[0]['#text']
                else:
                    word_type = span_node['#text']
            except:
                word_type = ''
            trans_item['itp_type'] = word_type
            trans_item['itp_str'] = word_dict.get('p').get('#text')
            trans_item['eap'] = []
            for example_item in item.css('div.examples '):
                example_sentence = '|'.join(example_item.css('p::text').extract())
                trans_item['eap'].append(example_sentence)
            output_item['itp'].append(trans_item)
        # write_obj_to_file('output.txt', output_item)
        # try:
        self.word_method(output_item)
        # except Exception as e:
        #     print(e)
        yield output_item


def crawl_update_word(word, option=2):
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    word_method = None
    if option == 1:
        word_method = write_obj_to_file
    elif option == 2:
        word_method = update_word
    process.crawl(YoudaoDictSpider, word=word, word_method=word_method)
    process.start()


if __name__ == '__main__':
    crawl_update_word('programmes', 2)
