from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField


class CreateWordForm(FlaskForm):
    word = StringField('word')
    interpretation = TextAreaField('interpretation')
    submit = SubmitField('Submit')


class UpdateWordForm(FlaskForm):
    word = StringField('word')
    interpretation = TextAreaField('interpretation')
    submit = SubmitField('Submit')


class PassageForm(FlaskForm):
    title = StringField('title')
    passage = TextAreaField('passage')
    submit = SubmitField('Submit')