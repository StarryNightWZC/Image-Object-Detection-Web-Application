from wtforms import Form, StringField, TextAreaField, PasswordField, validators, BooleanField, ValidationError
from flask_wtf import FlaskForm
from website.User import User


class RegistrationForm(Form):
    email= StringField('Email',[
        validators.Email(message="Your email format is incorrect"),
        validators.Length(min=6,max=50),
        #validators.none_of(values=CheckIFExist(), message="You have already registered, please log in")
    ])
    username=StringField('Username',[
        validators.Length(min=1,max=25),])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message="Passwords do not match"),
        validators.Length(min=6, max=255),
    ])
    confirm=PasswordField('Confirm Password')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already exists, please use a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Already Registered, Please use a different email address.')



class LoginForm(FlaskForm):
    username = StringField('Username', [
        validators.DataRequired(message="Plese input your username"),
        validators.Length(min=1, max=25),
    ])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.Length(min=6, max=255),
    ])