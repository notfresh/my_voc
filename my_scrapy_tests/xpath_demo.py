from scrapy.http import HtmlResponse as reponse

r = reponse(url='', body=open('./example.html').read().encode('utf-8'))
