# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

class MyPipeline(object):
    def process_item(self, item, spider):
        self.f.write(str(item) + '\n')
        return item

    def open_spider(self, spider):
        f = open('output.txt', 'a')
        self.f = f

    def close_spider(self, spider):
        self.f.close()




