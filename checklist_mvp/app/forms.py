# app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    matricula = StringField('Matrícula', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class AtivoForm(FlaskForm):
    codigo = StringField('Código do Ativo', validators=[DataRequired(), Length(min=2, max=64)])
    descricao = StringField('Descrição', validators=[DataRequired(), Length(min=5, max=200)])
    setor = StringField('Setor', validators=[DataRequired(), Length(min=3, max=120)])
    submit = SubmitField('Cadastrar Ativo')