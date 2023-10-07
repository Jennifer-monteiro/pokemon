from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, EqualTo

class PokeForm(FlaskForm):
    pokemon = StringField('Pokemon Name / Random Number', validators = [DataRequired()])
    submit = SubmitField('Search Pokemon')

class SignUpForm(FlaskForm):
    username= StringField(label='Username', validators=[DataRequired()])
    email= StringField("Email",[DataRequired()])
    password = PasswordField("Password", [DataRequired()])
    confirm_password = PasswordField("Confirm your password", [DataRequired(), EqualTo("password")])
    submit = SubmitField()

