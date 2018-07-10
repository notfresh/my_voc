from scrapy.crawler import CrawlerProcess, Crawler
from scrapy import Spider

from .spiders import YoudaoDictSpider
from scrapy.settings import Settings

# process = CrawlerProcess({
#     'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
# })





ITEM_PIPELINES = {
    'pipelines.MyPipeline': 300,
}
setting = Settings()
setting.set('ITEM_PIPELINES', ITEM_PIPELINES)
setting.set('USER_AGENT', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)')
process = CrawlerProcess(settings=setting)


word_list = ['mother', 'father']


process.crawl(Crawler(YoudaoDictSpider(word_list)))

if __name__ == '__main__':
    process.start()  # the script will block here until the crawling is finished
