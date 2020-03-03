from wtforms import StringField, PasswordField, SubmitField, validators
from wtforms.validators import DataRequired, Length, Email, ValidationError, EqualTo
from flask_wtf import FlaskForm

import mongodb_config as cfg
from pymongo import MongoClient

class LoginForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired(), Length(min = 5, max = 35)])
    password = PasswordField('Password', validators = [DataRequired(), Length(min = 5, max = 35)])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired(), Length(min = 5, max = 35)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min = 5, max = 35)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        client = MongoClient("mongodb+srv://"+ cfg.mongodb["username"] + ":" + cfg.mongodb["password"] + "@" + cfg.mongodb["host"])
        userdb = client.Users # the DB name is Users
        user = userdb.AddressBook_Users.find_one({"username": username.data})
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        client = MongoClient("mongodb+srv://"+ cfg.mongodb["username"] + ":" + cfg.mongodb["password"] + "@" + cfg.mongodb["host"])
        userdb = client.Users # the DB name is Users
        user = userdb.AddressBook_Users.find_one({"email": email.data})
        if user is not None:
            raise ValidationError('Please use a different email address.')