from flask_wtf import FlaskForm
from wtforms.fields.list import FieldList
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.fields.simple import StringField, SubmitField
from wtforms.fields import SelectMultipleField, MultipleFileField
from wtforms.validators import DataRequired


class AttendanceForm(FlaskForm):
    upload = FileField('Attendance', validators=[FileRequired(), FileAllowed(['xlsx', 'csv'], 'Images only!')])
    submit = SubmitField('Upload Attendance')


class MediaForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    type = StringField('Type', validators=[DataRequired()])
    media_url = MultipleFileField('Media URL', validators=[DataRequired()])
    submit = SubmitField('Upload Media')