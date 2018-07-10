from scrapy import Spider
from scrapy.crawler import CrawlerProcess


def write_obj_to_file(filename, obj):
    import json
    f = open(filename, 'a')
    f.write(json.dumps(obj)+ '\n')
    f.close()

# define a spider
class ShiyanlouCourseListSpider(Spider):
    name = 'shiyanlou_spider1'

    @property
    def start_urls(self):
        str_url_format = 'https://www.shiyanlou.com/courses/?category=all&course_type=all&fee=all&tag=all&page={}'
        return (str_url_format.format(i) for i in range(1, 2))  # 只爬第一页先

    def parse(self, response):
        courses_selector = response.css('div.content.course-items-container>div.row>div.course')
        for course in courses_selector:
            course_name = course.css('div.course-name::text').extract_first()
            course_desc = course.css('div.course-desc::text').extract_first()
            course_view_number = course.css('span.course-per-num::text')[1].re_first('[^\d]*(\d*)[^\d]*')
            dict_course = {}
            dict_course['course_name'] = course_name
            dict_course['course_desc'] = course_desc
            dict_course['course_view_number'] = course_view_number
            write_obj_to_file('output.txt', dict_course)
            yield dict_course


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})
if __name__ == '__main__':
    process.crawl(ShiyanlouCourseListSpider)
    process.start()  # the script will block here until the crawling is finished
