import time

from flask import render_template, request, redirect, url_for, flash

from app import db
from app.exceptions import DataError, error_dict
from app.models import Word, WordInterpretation, WordIPEAP, MyWord, Passage
from app.util import parse_word, word_to_str
from celery_tasks.tasks import crawl

from .form import CreateWordForm, UpdateWordForm, PassageForm
from . import voc


@voc.route('/words', methods=['GET'])
def words():
    page = request.args.get('page', 1, type=int)
    query = Word.query
    pagination = query.order_by(Word.created_at.desc()).paginate(page, per_page=10, error_out=False)
    words = pagination.items
    # 输出格式应该是 : { items: [ ], pages: [] }
    return render_template('vocabulary/words.html', pagination=pagination, words=words)


@voc.route('/words/<string:word>')
def word_detail(word):
    word_obj = Word.query.filter(Word.word == word).first()
    if not word_obj:
        flash('{} not exits!'.format(word))
        from_url = request.args.get('from')
        return redirect(from_url if from_url else url_for('main.index'))  # go back.
    return render_template('vocabulary/word_detail.html', word=word_obj)


@voc.route('/add_word', methods=['GET', 'POST'])
def add_word():
    format = '''example as follow:
    w: study
    itp: V-T/V-I | If you study, you spend time learning about a particular subject or subjects.
    eap: a relaxed and happy atmosphere that will allow you to study to your full potential.
    eap: He studied History and Economics.
    itp: N-UNCOUNT | Study is the activity of studying. | 学习
    eap: the use of maps and visual evidence in the study of local history.
    itp: N-COUNT | A study of a subject is a piece of research on it. 研究
    eap: Recent studies suggest that as many as 5 in 1,000 new mothers are likely to have this problem.
    itp: N-PLURAL | You can refer to educational subjects or courses that contain several elements as studies of a particular kind.| 学科
    '''
    create_word_form = CreateWordForm()
    if create_word_form.validate_on_submit():
        # word = create_word_form.word.data
        interpretation = create_word_form.interpretation.data
        dict_word = parse_word(interpretation)
        try:
            word_obj = Word.create_word(dict_word['w'], phonetics=dict_word.get('ph'), note=dict_word.get('n'))
            for itp_item in dict_word.get('itp') or []:
                itp_obj = WordInterpretation.create_word_interpretation(word_obj, itp_item['itp_type'],
                                                                        itp_item['itp_str'])
                for eap_item in itp_item.get('eap') or []:
                    WordIPEAP.create_word_ipeap(itp_obj, eap_item)
            return redirect(url_for('.word_detail', word=dict_word['w']))
        except DataError as e:
            flash(e.msg)
    return render_template('vocabulary/add_word.html', form=create_word_form, format=format)


@voc.route('/update_word/<string:word>', methods=['GET', 'POST'])
def update_word(word):
    form = UpdateWordForm()
    if request.method == 'GET':
        w = Word.query.filter(Word.word == word).first()
        word_str = request.form.get('interpretation') or word_to_str(w)
        form.interpretation.data = word_str
        return render_template('vocabulary/update_word.html', form=form, word_str=word_str, word=word)
    elif form.validate_on_submit():
        interpretation = form.interpretation.data
        try:
            dict_word = parse_word(interpretation)
            word_obj = db.session.query(Word).filter(Word.word == dict_word['w']).first()
            if not word_obj:
                raise DataError('WORD_NOT_FOUND', error_dict['WORD_NOT_FOUND'])
            db.session.query(WordIPEAP).filter(WordIPEAP.word_id == word_obj.id).delete()
            db.session.query(WordInterpretation).filter(WordInterpretation.word_id == word_obj.id).delete()
            for itp_item in dict_word.get('itp') or []:
                itp_obj = WordInterpretation.create_word_interpretation(word_obj, itp_item['itp_type'],
                                                                        itp_item['itp_str'])
                for eap_item in itp_item.get('eap') or []:
                    WordIPEAP.create_word_ipeap(itp_obj, eap_item)
            return redirect(url_for('.word_detail', word=word))
        except DataError as e:
            flash(e.msg)
            if e.code == 'WORD_NOT_FOUND':
                return redirect(url_for('.words'))
            else:
                return redirect(url_for('.update_word', word=word))


@voc.route('/delete_word/<string:word>', methods=['GET', 'POST'])
def delete_word(word):
    w = Word.query.filter(Word.word == word).first()
    if w:
        db.session.delete(w)
        flash('[{}] has been deleted.'.format(w.word))
    else:
        flash('[{}] not exits.'.format(w.word))
    return redirect(url_for('.words'))


@voc.route('/craw_word/<string:word>', methods=['GET', 'POST'])
def craw_word(word):
    crawl.delay(word, 2)  # 调用爬虫从有道翻译网站上爬取柯林斯词典.
    time.sleep(2)
    return redirect(url_for('.word_detail', word=word))


@voc.route('/mywords', methods=['GET'])
def mywords():
    page = request.args.get('page', 1, type=int)
    query = MyWord.query
    pagination = query.order_by(MyWord.created_at.desc()).paginate(page, per_page=200, error_out=False)
    words = pagination.items
    # 输出格式应该是 : { items: [ ], pages: [] }
    return render_template('vocabulary/mywords.html', pagination=pagination, words=words, title='My words')


@voc.route('/add_myword', methods=['GET', 'POST'])
def add_myword():
    format = '''  apple, bananas, pear, pineapple  '''
    create_word_form = CreateWordForm()
    if create_word_form.validate_on_submit():
        interpretation = create_word_form.interpretation.data
        list_words = [item.strip() for item in interpretation.strip().split(',')]
        for item in list_words:
            MyWord.create(item)
        return redirect(url_for('.mywords'))
    return render_template('vocabulary/add_myword.html', form=create_word_form, format=format)


@voc.route('/passages', methods=['GET'])
def passages():
    page = request.args.get('page', 1, type=int)
    query = db.session.query(Passage.id, Passage.title, Passage.passage_short)
    pagination = query.order_by(Passage.created_at.desc()).paginate(page, per_page=5, error_out=False)
    passages_list = pagination.items
    return render_template('vocabulary/passages.html', pagination=pagination, passages=passages_list, title='Passages')


@voc.route('/add_passage', methods=['GET', 'POST'])
def add_passage():
    form = PassageForm()
    if form.validate_on_submit():
        title = form.title.data
        passage = form.passage.data
        passage_obj = Passage.create(title, passage)
        return redirect(url_for('voc.passage_detail', passage_id=passage_obj.id))
    return render_template('vocabulary/add_passage.html', form=form, title='Add passage')


@voc.route('/passage_detail/<int:passage_id>', methods=['GET'])
def passage_detail(passage_id):
    passage_obj = db.session.query(Passage).filter(Passage.id == passage_id).first()
    if not passage_obj:
        flash('passage {} not exits'.format(passage_id))
        from_url = request.args.get('from')
        return redirect(from_url if from_url else url_for('main.index'))  # go back.
    return render_template('vocabulary/passage_detail.html', passage=passage_obj, title='Passage detail')



