__author__ = 'Cameron'
from flask_wtf import Form
from wtforms import StringField
from wtforms import PasswordField
from wtforms import BooleanField
from wtforms import validators


class RegistrationForm(Form):
    username = StringField('Username', [validators.required(), validators.length(min=4, max=25)])
    email = StringField('Email', [validators.email(), validators.length(min=6, max=35), validators.required()])
    password = PasswordField('Password', [
                                    validators.length(min=2), validators.required(),
                                    validators.equal_to('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    receive_emails = BooleanField('Would you like to receive morning update emails?', default=True)

class ChangePasswordForm(Form):
    password = PasswordField('Password', [validators.length(min=2), validators.required()])
    new_password = PasswordField('New Password', [validators.length(min=2), validators.required(),
                                    validators.equal_to('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat New Password')


class ChangeEmailForm(Form):
    password = PasswordField('Password', [validators.length(min=2), validators.required()])
    new_email = StringField('New Email', [
                                validators.email(), validators.length(min=6, max=35), validators.required()])