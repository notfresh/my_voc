import time
from datetime import datetime

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user

from app import db
from app.exceptions import DataError, error_dict
from app.models import Word, WordInterpretation, WordIPEAP, MyWord, Passage, MyUfWord, WordSet, WordSetSub
from app.util import parse_word, word_to_str
from app.util.parse_passage import *
from celery_tasks.tasks import crawl

from .form import CreateWordForm, UpdateWordForm, PassageForm, WordSetCreateForm, WordSetUpdateForm
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
        create_flag = request.args.get('create')
        if create_flag:
            word_obj = Word.create_word(word)
            crawl.delay(word, 2)  # 爬单词, 调用celery并不能省略参数，或者使用默认参数。
            flash('creating and crawling word in the background')
        return redirect(from_url if from_url else url_for('main.index'))  # go back.
    return render_template('vocabulary/word_detail.html', word=word_obj)


@voc.route('/words_modal/<string:word>')
def word_detail_modal(word):
    word_obj = Word.query.filter(Word.word == word).first()
    if not word_obj:
        create_flag = request.args.get('create')
        # if create_flag:
        word_obj = Word.create_word(word)
        crawl.delay(word, 2)  # 爬单词, 调用celery并不能省略参数，或者使用默认参数。
    return render_template('vocabulary/word_detail_modal.html', word=word_obj)


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
        # word_str = request.form.get('interpretation') or word_to_str(w)
        word_str = word_to_str(w)
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
    crawl.delay(word, 2)  # 调用爬虫从有道翻译网站上爬取柯林斯词典. 2 是固定用法， 就这写就完了。
    time.sleep(2)
    return redirect(url_for('.word_detail', word=word))


@voc.route('/mywords', methods=['GET'])
def mywords():
    page = request.args.get('page', 1, type=int)
    query = MyWord.query.filter(MyWord.user_id == current_user.id)
    pagination = query.order_by(MyWord.created_at.desc(), MyWord.word.asc()).paginate(page, per_page=200, error_out=False)
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
            MyWord.create(item, user_id=current_user.id)
        return redirect(url_for('.mywords'))
    return render_template('vocabulary/add_myword.html', form=create_word_form, format=format)


@voc.route('/passages', methods=['GET'])
def passages():
    page = request.args.get('page', 1, type=int)
    search_title = request.args.get('title')
    query = db.session.query(Passage.id, Passage.title, Passage.passage_short)
    if search_title:
        query = query.filter(Passage.title.like('%' + search_title + '%'))
    else:
        search_title = 'NULL'
    pagination = query.order_by(Passage.created_at.desc()).paginate(page, per_page=10, error_out=False)
    passages_list = pagination.items
    return render_template('vocabulary/passages.html',
                           pagination=pagination,
                           passages=passages_list,
                           title='Passages',
                           search_title=search_title)


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
    word_lists = passage_to_word_list(passage_obj.passage)
    word_lists = filter_word_list(word_lists)
    word_dict = statistic(word_lists)
    list_my_words_query = db.session.query(MyWord.word).filter(MyWord.user_id == current_user.id).all()
    list_my_words = [item[0] for item in list_my_words_query]
    word_dict = filter_my_words(word_dict, list_my_words)
    word_dict_list = sorted(word_dict.items(), key=lambda item: (item[1], item[0]), reverse=True)
    return render_template('vocabulary/passage_detail.html', passage=passage_obj,
                           title='Passage detail', word_dict_list=word_dict_list)


@voc.route('/update_passage/<int:passage_id>', methods=['GET', 'POST'])
def update_passage(passage_id):
    form = PassageForm()
    passage_obj = db.session.query(Passage).filter(Passage.id == passage_id).first()
    if request.method == 'GET':
        form.title.data = passage_obj.title
        form.passage.data = passage_obj.passage
        return render_template('vocabulary/update_passage.html', form=form, passage_id=passage_id, passage= passage_obj)
    elif form.validate_on_submit():
        title = form.title.data
        passage = form.passage.data
        try:
            passage_obj.title = title
            passage_obj.passage = passage
            passage_obj.updated_at = datetime.now()
            db.session.add(passage_obj)
            return redirect(url_for('.passage_detail', passage_id=passage_id))
        except Exception as e:
            db.session.rollback()
            flash(str(e))
            return redirect(url_for('.passage_detail', passage_id=passage_id))


@voc.route('/delete_passage/<int:passage_id>', methods=['GET', 'POST'])
def delete_passage(passage_id):
    p = Passage.query.filter(Passage.id == passage_id).first()
    if p:
        db.session.delete(p)
        flash('[{}] has been deleted.'.format(p.title))
    else:
        flash('[{}] not exits.'.format(p.title))
    return redirect(url_for('.passages'))


@voc.route('/myufwords', methods=['GET'])
def myufwords():
    page = request.args.get('page', 1, type=int)
    query = MyUfWord.query
    pagination = query.order_by(MyUfWord.created_at.desc()).paginate(page, per_page=200, error_out=False)
    words = pagination.items
    # 输出格式应该是 : { items: [ ], pages: [] }
    return render_template('vocabulary/myufwords.html', pagination=pagination, words=words, title='My unfamiliar words')


@voc.route('/add_myufword', methods=['GET', 'POST'])
def add_myufword():
    format = '''  newsstands, glamourous, pear, pineapple  '''
    create_word_form = CreateWordForm()
    if create_word_form.validate_on_submit():
        interpretation = create_word_form.interpretation.data
        list_words = [item.strip() for item in interpretation.strip().split(',')]
        for item in list_words:
            MyUfWord.create(item, user_id=current_user.id)
        return redirect(url_for('.myufwords'))
    return render_template('vocabulary/add_myword.html', form=create_word_form, format=format)


@voc.route('/add_myufword_api', methods=['POST'])
def add_myufword_api():
    data = request.get_json()
    words_str = request.get_json().get('selectedWordsStr')
    list_words = [item.strip() for item in words_str.strip().split(',')]
    for item in list_words:
        item_exist = db.session.query(MyUfWord).filter(MyUfWord.word == item).first()
        if not item_exist:
            MyUfWord.create(item, user_id=current_user.id)
    return jsonify({'status': 'OK'})


@voc.route('/add_my_familiar_word_api', methods=['POST'])
def add_my_familiar_word_api():
    words = request.get_json().get('words')
    list_words = [item.strip() for item in words]
    for item in list_words:
        item_exist = db.session.query(MyWord).filter(MyWord.word == item, MyWord.user_id == current_user.id).first()
        if not item_exist:
            MyWord.create(item, user_id=current_user.id)
    return jsonify({'status': 'OK'})


@voc.route('/delete_my_familiar_word_api', methods=['POST'])
def delete_my_familiar_word_api():
    words = request.get_json().get('words')
    list_words = [item.strip() for item in words]
    for item in list_words:
        item_exist = db.session.query(MyWord).filter(MyWord.word == item, MyWord.user_id == current_user.id).first()
        if item_exist:
            db.session.delete(item_exist)
    db.session.commit()
    return jsonify({'status': 'OK'})


@voc.route('/delete_myufwords', methods=['GET', 'POST'])
def delete_myufwords():
    format = '''  newsstands, glamourous, pear, pineapple , to be deleted!! '''
    create_word_form = CreateWordForm()
    if create_word_form.validate_on_submit():
        interpretation = create_word_form.interpretation.data
        list_words = [item.strip() for item in interpretation.strip().split(',')]
        for item in list_words:
            MyUfWord.query.filter(MyUfWord.word == item).delete()
        return redirect(url_for('.myufwords'))
    return render_template('vocabulary/delete_myufwords.html', form=create_word_form, format=format)


@voc.route('/word_sets', methods=['GET', 'POST'])
def word_sets():
    page = request.args.get('page', 1)
    per_page = 10
    title = 'Word set'
    pagination = db.session.query(WordSet).paginate(page=page, per_page=per_page, error_out=False)
    word_sets = pagination.items
    for item in word_sets:
        words = db.session.query(Word.word).join(WordSetSub, Word.id == WordSetSub.word_id)\
            .filter(WordSetSub.set_id == item.id).order_by(WordSetSub.created_at.asc()).limit(5).all()
        item.words = words
    return render_template('vocabulary/word_sets.html', title=title, pagination=pagination,  word_sets=word_sets)


@voc.route('/add_word_set', methods=['POST', 'GET'])
def add_word_set():
    format = '''  newsstands, news, newspaper'''
    title = 'Add word set'
    form = WordSetCreateForm()
    if form.validate_on_submit():
        set_title = form.set_title.data
        set_desc = form.set_desc.data
        set_words = form.set_words.data
        word_set_obj = WordSet.create(set_title, set_desc)
        list_words = [item.strip() for item in set_words.strip().split(',')]
        for item in list_words:
            word_obj = db.session.query(Word.word, Word.id).filter(Word.word == item).first()
            if not word_obj:
                flash('{} not exits'.format(item))
                return redirect(url_for('.word_sets'))
            WordSetSub.create(word_obj.id, word_set_obj.id)
        return redirect(url_for('.word_sets'))
    return render_template('vocabulary/add_word_set.html', form=form, title=title, format=format)


@voc.route('/word_set_detail/<int:id>', methods=['POST', 'GET'])
def word_set_detail(id):
    title = 'Update word set'
    form = WordSetUpdateForm()
    word_set_obj = db.session.query(WordSet).filter(WordSet.id == id).first()
    if request.method == 'GET':
        words = db.session.query(Word.word).join(WordSetSub, Word.id == WordSetSub.word_id) \
            .filter(WordSetSub.set_id == word_set_obj.id).all()
        form.set_words.data = ','.join([ item[0] for item in words])
        form.set_title.data = word_set_obj.set_title
        form.set_desc.data = word_set_obj.set_desc
        return render_template('vocabulary/word_set_detail.html', form=form, title=title)



