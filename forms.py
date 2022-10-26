from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired, FileField
from wtforms import StringField, SubmitField, EmailField, PasswordField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class Register(FlaskForm):
    f_name = StringField(label="First Name", validators=[DataRequired(), Length(min=1, max=49)])
    l_name = StringField(label="Last Name", validators=[DataRequired(), Length(min=1, max=49)])
    email = EmailField(label="Email", validators=[Email(), DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired(), EqualTo('confirm_password',
                                                                                   message='Passwords must match')])
    confirm_password = PasswordField(label="Confirm Password")
    photo = FileField("Photo", validators=[FileAllowed(['jpg', 'jpeg', 'png'], "Images Only!"), FileRequired()])
    accept_tos = BooleanField("I Accept Terms Of Service", validators=[DataRequired()])
    submit = SubmitField(label="Create My Account")


class LoginForm(FlaskForm):
    email = EmailField(label="Email", validators=[Email(), DataRequired()])
    password = PasswordField(label="Password")
    submit = SubmitField(label="Let Me In")


class AddProductForm(FlaskForm):
    item_name = StringField(label="Item Name", validators=[DataRequired()])
    description = TextAreaField(label="Description", validators=[DataRequired()])
    price = StringField(label="Price", validators=[DataRequired()])
    item_photo = StringField(label="Item Photo", validators=[DataRequired()])
    submit = SubmitField(label="Add")
