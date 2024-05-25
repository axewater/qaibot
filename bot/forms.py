from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class ChatForm(FlaskForm):
    question = StringField('Question', validators=[DataRequired()])
    submit = SubmitField('Send')
    magic = SubmitField('Magic')