from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

class UserForm(FlaskForm):
    nome = StringField('Nome Completo', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirm_senha = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('senha')])
    cargo = SelectField('Cargo', choices=[('COLABORADOR', 'Colaborador'), ('GESTOR', 'Gestor'), ('COORDENADOR', 'Coordenador')], validators=[DataRequired()])
    setor = SelectField('Setor', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Cadastrar Usuário')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este e-mail já está em uso. Escolha outro.')

class SectorForm(FlaskForm):
    nome = StringField('Nome do Setor', validators=[DataRequired()])
    submit = SubmitField('Cadastrar Setor')

class EquipmentForm(FlaskForm):
    nome = StringField('Nome do Equipamento', validators=[DataRequired()])
    setor = SelectField('Setor', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Cadastrar Equipamento')