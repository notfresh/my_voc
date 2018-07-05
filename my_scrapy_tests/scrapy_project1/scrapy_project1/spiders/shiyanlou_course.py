# -*- coding: utf-8 -*-
import scrapy


class ShiyanlouCourseSpider(scrapy.Spider):
    name = 'shiyanlou_course_spider'
    allowed_domains = ['shiyanlou.com']

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
