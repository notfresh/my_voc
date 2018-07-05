'''
说明:
目的是爬一下实验楼的课程页面.
爬取的范围是固定格式的URL:  https://www.shiyanlou.com/courses/?category=all&course_type=all&fee=all&tag=all&page={}
page范围 从1-22

写完之后, 运行spider:
scrapy runspider my_scrapy_tests/crawl_shiyanlou_demo1.py -o data.json  # 输出格式为 json, 看到的文件是unicode编码的
scrapy runspider my_scrapy_tests/crawl_shiyanlou_demo1.py -o output.xml  # 输出格式为 .xml, 看到的汉子比较清楚.


def start_requests(self):
    # 课程列表页面 url 模版
    url_tmpl = 'https://www.shiyanlou.com/courses/?category=all&course_type=all&fee=all&tag=all&page={}'
    # 所有要爬取的页面
    urls = (url_tmpl.format(i) for i in range(1, 23))
    # 返回一个生成器，生成 Request 对象，生成器是可迭代对象
    for url in urls:
        yield scrapy.Request(url=url, callback=self.parse)


'''
from scrapy import Spider


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
            yield dict_course
