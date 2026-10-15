from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, DateField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, NumberRange, Optional
from wtforms import SelectMultipleField, widgets, RadioField, TimeField

class OnboardingForm(FlaskForm):
    user_type = RadioField('I am', choices=[
        ('isc', 'An ISC student (Class 11 or 12)'),
        ('general', 'Tracking my own subjects or projects'),
    ], default='isc')
    class_level = SelectField('Class', choices=[('11', 'Class 11'), ('12', 'Class 12')], validators=[Optional()])
    subjects = SelectMultipleField(
        'Your Subjects',
        coerce=int,
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False)
    )
    submit = SubmitField('Continue')
    
class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class TaskForm(FlaskForm):
    subject_id = SelectField('Subject', coerce=int, validators=[Optional()])
    custom_subject = StringField('Or type your own subject', validators=[Optional(), Length(max=100)])
    chapter_id = SelectField('Chapter', coerce=int, validators=[Optional()])
    custom_chapter = StringField('Or type your own chapter', validators=[Optional(), Length(max=150)])
    tasktype = StringField('Task Type', validators=[Optional(), Length(max=100)])
    deadline = DateField('Deadline', validators=[Optional()], format='%Y-%m-%d')
    difficulty = SelectField('Difficulty', choices=[('1', '1 - Easy'), ('2', '2'), ('3', '3 - Medium'), ('4', '4'), ('5', '5 - Hard')], validators=[DataRequired()])
    time_required = IntegerField('Time Required (minutes)', validators=[Optional(), NumberRange(min=1)])
    split_count = IntegerField('Split into how many sessions?', validators=[Optional(), NumberRange(min=1, max=10)])
    submit = SubmitField('Save Task')

from wtforms import SelectMultipleField, widgets, TimeField

class FixedCommitmentForm(FlaskForm):
    label = StringField('What is this?', validators=[DataRequired(), Length(max=100)])
    days = SelectMultipleField(
        'Which days?',
        choices=[('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), ('3', 'Thursday'),
                 ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')],
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False)
    )
    start_time = TimeField('Start time', validators=[DataRequired()])
    end_time = TimeField('End time', validators=[DataRequired()])
    color = StringField('Color', validators=[Optional()])
    submit_fixed = SubmitField('Add Commitment')
    

class SleepForm(FlaskForm):
    start_time = TimeField('Sleep time', validators=[DataRequired()])
    end_time = TimeField('Wake time', validators=[DataRequired()])
    submit_sleep = SubmitField('Save Sleep Schedule')

class OneOffCommitmentForm(FlaskForm):
    label = StringField('What is this?', validators=[DataRequired(), Length(max=100)])
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    start_time = TimeField('Start time', validators=[DataRequired()])
    end_time = TimeField('End time', validators=[DataRequired()])
    subject_id = SelectField('Related subject (optional)', coerce=int, validators=[Optional()])
    color = StringField('Color', validators=[Optional()])
    submit_oneoff = SubmitField('Add One-Off Commitment')