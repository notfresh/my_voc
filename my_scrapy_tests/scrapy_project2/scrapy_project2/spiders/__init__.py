# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import re

import xmltodict
from scrapy.spiders import CrawlSpider


class YoudaoDictSpider(CrawlSpider):
    name = 'youdao_dict_spider'

    def __init__(self, word_list=None):
        if word_list:
            self.word_list = word_list
        else:
            self.word_list = ['word', 'apple', 'sugar']

        url = 'http://dict.youdao.com/w/eng/{}/'
        self.start_urls = [url.format(item) for item in self.word_list]
        super().__init__()

    def parse(self, response):
        trans = response.css('div#authTrans div#collinsResult ul.ol>li')
        request_url = response.__dict__['_url']
        word = re.findall('^.*/(\w+)/$', request_url)[0]
        output_item = {'word': word, 'trans': []}
        for item in trans:
            # 翻译
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
            trans_item['type'] = word_type
            trans_item['text'] = word_dict.get('p').get('#text')
            trans_item['examples'] = []
            for example_item in item.css('div.examples '):
                example_sentence = '|'.join(example_item.css('p::text').extract())
                trans_item['examples'].append(example_sentence)
            output_item['trans'].append(trans_item)
        yield output_item