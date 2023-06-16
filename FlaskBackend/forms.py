from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField,DateField
from wtforms.validators import DataRequired, Email, EqualTo


class RegistrationForm(FlaskForm):
  
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    income = StringField('income', validators=[DataRequired()])
    weekly_availability = StringField('weekly_availability', validators=[DataRequired()])
    nic = StringField('nic', validators=[DataRequired()])
    emp_status = StringField('emp_status', validators=[DataRequired()])
    gender = StringField('Gender', validators=[DataRequired()])
    al_subject1 = StringField('AL Subject 1', validators=[DataRequired()])
    al_subject2 = StringField('AL Subject 2', validators=[DataRequired()])
    al_subject3 = StringField('AL Subject 3', validators=[DataRequired()])
    ol_subject1 = StringField('OL Subject 1', validators=[DataRequired()])
    ol_subject2 = StringField('OL Subject 2', validators=[DataRequired()])
    ol_subject3 = StringField('OL Subject 3', validators=[DataRequired()])
    ol_subject4 = StringField('OL Subject 4', validators=[DataRequired()])
    ol_subject5 = StringField('OL Subject 5', validators=[DataRequired()])
    ol_subject6 = StringField('OL Subject 6', validators=[DataRequired()])
    ol_subject7 = StringField('OL Subject 7', validators=[DataRequired()])
    ol_subject8 = StringField('OL Subject 8', validators=[DataRequired()])
    ol_subject9 = StringField('OL Subject 9', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    userRole = StringField('User Role', validators=[DataRequired()])
    married = StringField('married')
    birthday = DateField('Birthday', format='%Y-%m-%d', validators=[DataRequired()])
    stream = StringField('stream', validators=[DataRequired()])
    passedList = StringField('Passed List')
    eligibleOnly = StringField('Eligible Only')
    pendingEligible = StringField('Pending Eligible')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])