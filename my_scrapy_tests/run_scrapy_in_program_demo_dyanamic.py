import re

import xmltodict
from scrapy import Spider
from scrapy.crawler import CrawlerProcess


def write_obj_to_file(filename, obj):
    import json
    f = open(filename, 'a')
    f.write(json.dumps(obj) + '\n')
    f.close()


# define a spider
class YoudaoDictSpider(Spider):
    name = 'shiyanlou_spider1'

    def __init__(self, word_list=None):
        super().__init__()
        if word_list:
            self.word_list = word_list
        else:
            self.word_list = ['word', 'apple', 'sugar']

        url = 'http://dict.youdao.com/w/eng/{}/'
        self.start_urls = [url.format(item) for item in self.word_list]

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
        write_obj_to_file('output.txt', output_item)
        yield output_item


def crawl_word_trans_from_youdao(word_list):
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(YoudaoDictSpider, word_list=word_list)
    process.start()  # the script will block here until the crawling is finished


if __name__ == '__main__':
    crawl_word_trans_from_youdao(['good'])
