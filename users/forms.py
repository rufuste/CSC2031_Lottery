import re

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.fields.html5 import TelField
from wtforms.validators import Required, Email, Length, EqualTo, ValidationError


# Checks only valid name characters present - no symbols
def character_check_name(form, field):
    excluded_chars = "*?!'^+%&/()=}][{$#@<>"
    for char in field.data:
        if char in excluded_chars:
            raise ValidationError(
                f"Character {char} is not allowed.")


# Checks only valid password characters present
def character_check_pass(form, field):
    excluded_chars = "*?"
    for char in field.data:
        if char in excluded_chars:
            raise ValidationError(
                f"Character {char} is not allowed.")


class RegisterForm(FlaskForm):
    # Validators ensure register input for each field is as expected
    email = StringField(validators=[Required(), Email()])
    firstname = StringField(validators=[Required(), character_check_name])
    lastname = StringField(validators=[Required(), character_check_name])
    phone = TelField(validators=[Required()])
    password = PasswordField(validators=[Required(),
                                         Length(min=6, max=12,
                                                message='Password must be between 6 and 12 characters in length.'),
                                         character_check_pass])
    confirm_password = PasswordField(
        validators=[Required(), EqualTo('password', message='Both password fields must be equal!')])
    pin_key = StringField(
        validators=[Required(), character_check_pass, Length(max=32, min=32, message="Length of PIN key must be 32.")])
    submit = SubmitField()

    # Checks password field against regex, called implicitly
    def validate_password(self, password):
        p = re.compile(r"(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[-+_!@#$%^&*.,?])")
        if not p.match(self.password.data):
            raise ValidationError("Password must contain at least 1 digit, 1 uppercase letter, 1 lowercase and one "
                                  "symbol.")

    # Checks phone field against expected regex, called implicitly
    def validate_phone(self, phone):
        p = re.compile(r'[0-9]{4}-[0-9]{3}-[0-9]{4}')
        if not p.match(self.phone.data):
            raise ValidationError("Phone must take form XXXX-XXX-XXXX (including the dashes)")


# Login form checks validation before submitting the form data
class LoginForm(FlaskForm):
    email = StringField(validators=[Required(), Email()])
    password = PasswordField(validators=[Required()])
    pin = StringField(validators=[Required(), Length(min=6, max=6, message='PIN Must be 6 characters long')])
    submit = SubmitField()
