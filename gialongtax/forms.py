from flask_wtf import FlaskForm, RecaptchaField
from wtforms import SelectField, StringField, PasswordField, SubmitField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from gialongtax.models import User, Post


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
                        DataRequired(), Email(), Length(min=6, max=30)])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=9, max=50)])
    #recaptcha = RecaptchaField()
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    fullname = StringField('User Full name', validators=[
                           DataRequired(), Length(min=4, max=30)])
    email = StringField('Email', validators=[
                        DataRequired(), Email(), Length(min=6, max=30)])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=9, max=50)])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')])
    #recaptcha = RecaptchaField()
    submit = SubmitField('Sign Up')

    def validate_username(self, fullname):
        user = User.query.filter_by(fullname=fullname.data).first()
        if user:
            raise ValidationError(
                'That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                'That email is taken. Please choose a different one.')


class ContactForm(FlaskForm):
    username = StringField('User Full name', validators=[DataRequired(), Length(min=4, max=30)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=30)])
    subject = StringField('Subject', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=20)])
    #recaptcha = RecaptchaField()
    submit = SubmitField('Send Us')

class PostForm(FlaskForm):
    posttyle = SelectField('Chọn thể loại', validate_choice=False, choices=[(0, 'Chọn thể loại'), (1, 'NEWS'), (2, 'SERVICES'), (3, 'CUSTOMERS')])
    title = StringField('Title', validators=[DataRequired(), Length(min=20)])
    content = TextAreaField('Content', validators=[
                            DataRequired(), Length(min=50)])
    submit = SubmitField('News Post')

    def validate_posttyle(self, posttyle):
        if int(posttyle.data)<1:
            raise ValidationError('Chọn thể loại bài cần đăng')
