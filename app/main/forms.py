from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FloatField, ValidationError
from wtforms.validators import DataRequired, Length, Regexp, NumberRange

from ..models import Promoter_library, Plan, Sequence
from flask_login import current_user


class PromLibForm(FlaskForm):
    name_lib = StringField('Library', validators=[DataRequired(), Length(1,64)])
    submit_lib = SubmitField('Create')

    def validate_name_lib(self, field):
        if Promoter_library.query.filter_by(name=field.data, creator_lib=current_user._get_current_object()).first():
            raise ValidationError('Library name already exists.')

class PromPlanForm(FlaskForm):
    name_plan = StringField('Plan', validators=[DataRequired(), Length(1,64)])
    plan = StringField('Blueprint', validators=[DataRequired(), Length(50,50, "Field must be 50 characters long."),
                                                Regexp('[ACTGacgtRYKMSWBDHVN]*$', 0,
                                                       'Blueprint can only have specified letters')])
    treshold = StringField('Treshold', validators=[])
    submit_plan = SubmitField('Create')

    def validate_name_plan(self, field):
        if Plan.query.filter_by(name=field.data, creator_plan=current_user._get_current_object()).first():
            raise ValidationError('Blueprint name already exists.')


class PromSeqForm(FlaskForm):
    name_seq = StringField('Sequence', validators=[DataRequired(), Length(1,64)])
    plan = StringField('Blueprint', validators=[DataRequired(), Length(50),
                                                Regexp('[ACTGacgtRYKMSWBDHVN]*$', 0,
                                                       'Blueprint can only have specified letters')])
    library = StringField('Library', validators=[DataRequired(), Length(1,64)])
    submit_seq = SubmitField('Create')

    def validate_name_seq(self, field):
        Library = Promoter_library.query.filter_by(name=self.library.data, creator_lib=current_user._get_current_object()).first()
        if Sequence.query.filter_by(name=field.data, library_seq=Library, creator_seq=current_user._get_current_object()).first():
            raise ValidationError('Sequence name already exists.')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1,64)])
    body = TextAreaField("Post", validators=[DataRequired()])
    submit_post = SubmitField('Post')