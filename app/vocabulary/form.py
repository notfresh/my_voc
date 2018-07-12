from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, validators


class CreateWordForm(FlaskForm):
    word = StringField('word')
    interpretation = TextAreaField('interpretation')
    submit = SubmitField('Submit')


class UpdateWordForm(FlaskForm):
    word = StringField('word')
    interpretation = TextAreaField('interpretation')
    submit = SubmitField('Submit')


class PassageForm(FlaskForm):
    title = StringField('title', validators=[validators.input_required()])
    passage = PageDownField('passage', validators=[validators.input_required()])
    submit = SubmitField('Submit')


class WordSetCreateForm(FlaskForm):
    set_title = StringField('Set title')
    set_desc = StringField('Set description')
    set_words = TextAreaField('words in the set')
    submit = SubmitField()


class WordSetUpdateForm(FlaskForm):
    set_title = StringField('Set title')
    set_desc = StringField('Set description')
    set_words = TextAreaField('words in the set')
    add_words = TextAreaField('words to add ')
    delete_words = TextAreaField('words to delete')
    submit = SubmitField()

