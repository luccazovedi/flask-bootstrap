from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from wtforms import StringField, SubmitField, PasswordField, SelectField, BooleanField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from dotenv import load_dotenv
import os
import requests

# ---------- CONFIGURAÇÃO ----------
app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
load_dotenv()
app.secret_key = "chave-secreta"

# Configurações do Mailgun
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAILGUN_BASE_URL = "https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
MAILGUN_EMAIL = "postmaster@{MAILGUN_DOMAIN}"
# ---------- ENVIO DE E-MAIL ----------
def enviar_email_mailgun(destinatario, assunto, corpo):
    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": f"Aplicação Flask Lucca Zovedi <{MAILGUN_EMAIL}>",
                "to": [destinatario],
                "subject": assunto,
                "text": corpo,
            },
        )
        print("Status:", response.status_code)
        print("Resposta:", response.text)
        return response
    except Exception as e:
        print("Erro ao enviar e-mail:", e)
# ---------- FORMULÁRIOS ----------
class CadastroForm(FlaskForm):
    nome = StringField("Nome do Usuário", validators=[DataRequired()])
    enviar_email = BooleanField("Enviar e-mail para flaskaulasweb@zohomail.com")
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

# ---------- ROTAS ----------
@app.route("/")
def index():
    return render_template("index.html", current_time=datetime.utcnow())

@app.route("/user/<name>")
def user(name):
    return render_template("user.html", name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Identificação
@app.route("/user/<name>/<institution>/<course>")
def identify(name, institution, course):
    return render_template("identify.html", name=name, institution=institution, course=course)

# Contexto Requisição
@app.route("/request/<name>")
def request_context(name):
    return render_template("request.html", name=name)

# Contexto Formulário
@app.route('/forms', methods=['GET', 'POST'])
def forms():
    form = NomeForm()
    nome = sobrenome = instituicao = disciplina = ''

    if form.validate_on_submit():
        nome = form.nome.data
        sobrenome = form.sobrenome.data
        instituicao = form.instituicao.data
        disciplina = form.disciplina.data

    return render_template('forms.html', form=form, nome=nome, sobrenome=sobrenome, instituicao=instituicao, disciplina=disciplina)

# Login
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario = form.usuario.data
        return redirect(url_for('loginResponse', usuario=usuario))
    return render_template('login.html', form=form)

@app.route("/loginResponse/<usuario>")
def loginResponse(usuario):
    return render_template('loginResponse.html', usuario=usuario)

usuarios = [
    {"nome": "Lucca", "funcao": "Administrador"},
    {"nome": "Zovedi", "funcao": "User"},
    {"nome": "Lucca Zovedi", "funcao": "Moderador"},
]

@app.route("/listausuario", methods=["GET", "POST"])
def listausuario():
    nome = None
    funcao = None

    if request.method == "POST":
        nome = request.form.get("nome")
        funcao = request.form.get("funcao")

        if nome and funcao:
            usuarios.append({"nome": nome, "funcao": funcao})

    return render_template(
        "listausuario.html",
        nome=nome,
        funcao=funcao,
        usuarios=usuarios
    )

# Cadastro
usuarios_cadastrados = [
    {"nome": "Lucca", "funcao": "Administrador"}
]

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    form = CadastroForm()
    nome_usuario = None
    mensagem_extra = None

    if form.validate_on_submit():
        nome_usuario = form.nome.data.strip()
        funcao = "Administrador" if nome_usuario.lower() == "lucca" else "User"

        # Adiciona usuário
        usuarios_cadastrados.append({"nome": nome_usuario, "funcao": funcao})

        # Flash temporário de boas-vindas
        flash(f"Olá, {nome_usuario}!\nCadastro realizado com sucesso!", "success")

        # Se marcar envio de e-mail
        if form.enviar_email.data:
            corpo_email = f"""Prontuário: PT3036463
Nome do aluno: Lucca Zovedi
Usuário cadastrado: {nome_usuario}"""
            resposta = enviar_email_mailgun(
                destinatario="flaskaulasweb@zohomail.com",
                assunto="Novo usuário cadastrado - Flask Aulas Web",
                corpo=corpo_email
            )
            if resposta.status_code == 200:
                # Mensagem fixa exibida no HTML
                mensagem_extra = "Prazer em conhecê-lo!\n\nE-mail enviado para o Administrador do sistema, notificando o cadastro de um novo usuário."
                flash("✅ E-mail enviado com sucesso!", "info")
            else:
                flash(f"❌ Falha ao enviar e-mail ({resposta.status_code})", "danger")

        # Limpar formulário
        form.nome.data = ""
        form.enviar_email.data = False

    return render_template(
        "cadastro.html",
        form=form,
        usuarios=usuarios_cadastrados,
        nome_envio=nome_usuario,
        mensagem_extra=mensagem_extra
    )


# ---------- EXECUÇÃO ----------
if __name__ == '__main__':
    app.run(debug=True)