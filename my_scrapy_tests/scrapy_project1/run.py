from scrapy.crawler import CrawlerProcess
from scrapy import Spider

from scrapy_project1.spiders.shiyanlou_course import ShiyanlouCourseSpider # 编辑器的提示是错的. 编译器的智能导入也不一定绝对可靠.

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

process.crawl(ShiyanlouCourseSpider())

if __name__ == '__main__':
    process.start()  # the script will block here until the crawling is finished
