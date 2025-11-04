from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Optional


class CadastroForm(FlaskForm):
    prontuario = StringField('Prontuário', validators=[Optional()])
    nome = StringField("Nome do Usuário", validators=[DataRequired()])
    email = StringField('E-mail', validators=[Optional(), Email()])
    submit = SubmitField("Cadastrar")


class NomeForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    sobrenome = StringField('Sobrenome', validators=[DataRequired()])
    instituicao = StringField('Instituição', validators=[DataRequired()])
    disciplina = SelectField('Disciplina', choices=[
        ('', 'Escolha uma Disciplina'),
        ('DSWA5', 'DSWA5'),
        ('DWBA4', 'DWBA4'),
        ('Gestão de Projetos', 'Gestão de Projetos')
    ], validators=[DataRequired()])
    submit = SubmitField('Enviar')


class LoginForm(FlaskForm):
    usuario = StringField('Usuário ou E-mail', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')
