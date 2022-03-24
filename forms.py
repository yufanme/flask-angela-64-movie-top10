from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class EditForm(FlaskForm):
    change_rating = StringField(label="Your Rating Out of 10 e.g. 7.5", validators=[DataRequired()])
    change_review = StringField(label="Your Review", validators=[DataRequired()])
    submit_button = SubmitField(label="Down")


class AddForm(FlaskForm):
    movie_title = StringField(label="Movie Title", validators=[DataRequired()])
    submit_button = SubmitField(label="Add Movie")
