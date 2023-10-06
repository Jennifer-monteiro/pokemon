from flask import Flask
from config import Config
	
app = Flask(__name__)
app.config.from_object(Config)

from . import routes
app.static_folder = 'static'

from wtforms import Form, BooleanField, StringField, PasswordField, validators

""" class SignUp(Form):
    username= StringField('Username', [validators.Length(min=4,max=25)])
    username= StringField('Username',[validators.Length(min=6,max=35)])
    email=PasswordField("New Password",
 """
