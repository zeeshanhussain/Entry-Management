from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp


class RegistrationForm(FlaskForm):
    name = StringField('Name',
                       validators=[DataRequired(), Length(min=2, max=30)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    mobile = StringField('Mobile Number',
                         validators=[DataRequired(), Length(min=10, max=10, message="Enter a 10 digit number. "),
                                     Regexp('^[0-9]*$', message="Mobile Numbers can only include numeric digits")])
    address = StringField('Address',
                          validators=[DataRequired(), Length(min=2, max=30)])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class CheckInForm(FlaskForm):
    name = StringField('Name',
                       validators=[DataRequired(), Length(min=2, max=30)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])

    mobile = StringField('Mobile Number',
                         validators=[DataRequired(), Length(min=10, max=10, message="Enter a 10 digit number. "),
                                     Regexp('^[0-9]*$', message="Mobile Numbers can only include numeric digits.")])
    host_id = SelectField(u'Select Host')

    submit = SubmitField('Check In')


class CheckOutForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Check Out')
