from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class CreateWordForm(FlaskForm):
    word = StringField('word')
    interpretation = StringField('interpretation')
    submit = SubmitField('Submit')
