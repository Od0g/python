# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import TipoAtivo

def tipos_ativo_query():
    return TipoAtivo.query

class LoginForm(FlaskForm):
    matricula = StringField('Matrícula', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class AtivoForm(FlaskForm):
    codigo = StringField('Código do Ativo', validators=[DataRequired(), Length(min=2, max=64)])
    descricao = StringField('Descrição', validators=[DataRequired(), Length(min=5, max=200)])
    setor = StringField('Setor', validators=[DataRequired(), Length(min=3, max=120)])
    tipo_ativo = QuerySelectField('Tipo de Ativo', query_factory=tipos_ativo_query, get_label='nome', allow_blank=False)
    submit = SubmitField('Salvar Ativo')

class CadastroUsuarioForm(FlaskForm):
    matricula = StringField('Matrícula', validators=[DataRequired()])
    nome = StringField('Nome Completo', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    perfil = SelectField('Perfil', choices=[('operador', 'Operador'), ('lider', 'Líder'), ('gestor', 'Gestor'), ('admin', 'Administrador')], validators=[DataRequired()])
    submit = SubmitField('Cadastrar Usuário')

class ModeloChecklistForm(FlaskForm):
    nome = StringField('Nome do Modelo', validators=[DataRequired()])
    descricao = TextAreaField('Descrição')
    submit = SubmitField('Salvar Modelo')

class ItemModeloForm(FlaskForm):
    pergunta = StringField('Texto da Pergunta', validators=[DataRequired()])
    submit = SubmitField('Adicionar Pergunta')