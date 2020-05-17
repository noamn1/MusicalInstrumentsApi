from wtforms import Form, BooleanField, StringField, PasswordField, validators
from wtforms.fields.html5 import EmailField


class RegistrationForm(Form):
    first_name = StringField('first_name', [validators.Length(min=4, max=25)])
    last_name = StringField('last_name', [validators.Length(min=4, max=25)])
    email = EmailField('email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')