from flask import render_template, request, redirect, url_for

from app import db
from app.models import Word, WordInterpretation
from .form import CreateWordForm
from . import voc


@voc.route('/words', methods=['GET', 'POST'])
def words():
    form = CreateWordForm()
    if form.validate_on_submit():
        word = form.word.data
        interpretation = form.interpretation.data
        # 希望获得的数据是这样的 n:if it'a a dog, i can bark;v: i dont know what it is .
        inters = [item.split(':') for item in interpretation.split(';')]
        word_obj = Word.create_word(word)
        for item in inters:
            WordInterpretation.create_word_interpretation(word_obj, item[0], item[1])
        db.session.commit()
        redirect(url_for('.words'))
    page = request.args.get('page', 1, type=int)
    """
    期望返回格式
    单条:
    {word: '', inters:[ {type: v, interpret: xxxx, examples: [ aaaa, bbbb, cccc ] }, {type: v, interpret: yyyy } ]}
    """
    query = Word.query
    pagination = query.order_by(Word.created_at.desc()).paginate(page, per_page=10, error_out=False )
    words = pagination.items
    # 输出格式应该是 : { items: [ ], pages: [] }
    return render_template('vocabulary/words.html', form=form, pagination=pagination, words=words)




@voc.route('/add_word', methods=['POST'])
def add_word():
    create_word_form = CreateWordForm()
    if create_word_form.validate_on_submit():
        word = create_word_form.word.data
        interpretation = create_word_form.interpretation.data
        # 希望获得的数据是这样的 n:if it'a a dog, i can bark;v: i dont know what it is .
        inters = [item.split(':') for item in  interpretation.split(';')]
        word_obj = Word.create_word(word)
        for item in inters:
            WordInterpretation.create_word_interpretation(word_obj, item[0], item[1])
        db.session.commit()
        redirect(url_for('.words'))



