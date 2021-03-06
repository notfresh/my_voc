from .craw_word import crawl_update_word
from .celery import app


@app.task
def crawl(word, method=2):
    crawl_update_word(word, method)
    return 0
