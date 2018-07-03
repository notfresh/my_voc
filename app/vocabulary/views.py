from flask import render_template, request, redirect, url_for, flash

from app import db
from app.exceptions import DataError
from app.models import Word, WordInterpretation, WordIPEAP
from app.util import parse_word, word_to_dict
from .form import CreateWordForm, UpdateWordForm
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
    word = Word.query.filter(Word.word == word).first()
    return render_template('vocabulary/word_detail.html', word=word)


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
            word_obj = Word.create_word(dict_word['w'])
            for itp_item in dict_word.get('itp') or []:
                itp_obj = WordInterpretation.create_word_interpretation(word_obj, itp_item['itp_type'], itp_item['itp_str'])
                for eap_item in itp_item.get('eap') or []:
                    WordIPEAP.create_word_ipeap(itp_obj, eap_item)
            return redirect(url_for('.words'))
        except DataError as e:
            flash(e.msg)
    return render_template('vocabulary/add_word.html', form=create_word_form, format=format)


@voc.route('/update_word/<string:word>', methods=['GET', 'POST'])
def update_word(word):
    form = UpdateWordForm()
    if request.method == 'GET':
        w = Word.query.filter(Word.word == word).first()
        word_str = word_to_dict(w)
        form.interpretation.data = word_str
        return render_template('vocabulary/update_word.html', form=form, word_str=word_str, word=word)
    elif form.validate_on_submit():





@voc.route('/delete_word/<string:word>', methods=['GET', 'POST'])
def delete_word(word):
    w = Word.query.filter(Word.word == word).first()
    if w:
        db.session.delete(w)
        flash('[{}] has been deleted.'.format(w.word))
    else:
        flash('[{}] not exits.'.format(w.word))
    return redirect(url_for('.words'))
