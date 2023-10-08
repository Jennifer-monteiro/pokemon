from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, validators
from wtforms.validators import DataRequired, EqualTo, Email


class PokeForm(FlaskForm):
    pokemon = StringField('Pokemon Name / Random Number', validators = [DataRequired()])
    submit = SubmitField('Search Pokemon')

class SignUpForm(FlaskForm):
    fullname = StringField('Full Name', validators=[validators.DataRequired()])
    username= StringField(label='Username', validators=[DataRequired()])
    email= StringField("Email",[DataRequired()])
    password = PasswordField("Password", [DataRequired()])
    confirm_password = PasswordField("Confirm your password", [DataRequired(), EqualTo("password")])
    submit = SubmitField()

class LoginForm(FlaskForm):
    username= StringField(label='Username', validators=[DataRequired()])
    password = PasswordField("Password", [DataRequired()])
    submit = SubmitField()

class ProfileForm(FlaskForm):
    new_username = StringField('New Username', validators=[DataRequired()])
    new_email = StringField('New Email', validators=[DataRequired(), Email()])
    submit_username = SubmitField('Save Username')
    submit_email = SubmitField('Save Email')