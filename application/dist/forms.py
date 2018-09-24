from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    login = StringField('', validators=[DataRequired()], render_kw={"placeholder": "Ваш корпоративний email"})
    password = PasswordField('', validators=[DataRequired()], render_kw={"placeholder": "Ваш корпоративний пароль"})


class LoginFormPoll(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])


