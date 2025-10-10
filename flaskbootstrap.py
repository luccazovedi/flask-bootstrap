from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from wtforms import StringField, SubmitField, PasswordField, SelectField
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

app.secret_key = os.getenv("FLASK_SECRET_KEY", "@996262502LZ")

# Configurações do Mailgun
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAILGUN_BASE_URL = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"

# ---------- ENVIO DE E-MAIL ----------
def send_user_registration_email(prontuario, nome, usuario, email_institucional):
    if not MAILGUN_API_KEY or not MAILGUN_DOMAIN:
        app.logger.error("MAILGUN_API_KEY ou MAILGUN_DOMAIN não configurados.")
        return False

    assunto = "Novo usuário cadastrado - Flask Aulas Web"
    corpo = f"""
Novo aluno cadastrado no sistema Flask Aulas Web:

📘 Prontuário: {prontuario}
👤 Nome: {nome}
💻 Usuário: {usuario}
📧 E-mail: {email_institucional}
"""
    destinatarios = f"flaskaulasweb@zohomail.com, luccazovedi@gmail.com"

    try:
        r = requests.post(
            MAILGUN_BASE_URL,
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": f"Flask Aulas Web <postmaster@{MAILGUN_DOMAIN}>",
                "to": destinatarios,
                "subject": assunto,
                "text": corpo
            },
            timeout=10
        )
        if r.status_code == 200 or r.status_code == 201:
            app.logger.info(f"E-mail enviado com sucesso para {destinatarios}")
            return True
        else:
            app.logger.error(f"Erro Mailgun ({r.status_code}): {r.text}")
            return False
    except Exception as e:
        app.logger.error(f"Falha ao enviar e-mail: {e}")
        return False


# ---------- FORMULÁRIOS ----------
class CadastroForm(FlaskForm):
    prontuario = StringField("Prontuário", validators=[DataRequired()])
    nome = StringField("Nome", validators=[DataRequired()])
    usuario = StringField("Usuário", validators=[DataRequired()])
    email = StringField("E-mail institucional", validators=[DataRequired()])
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
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    form = CadastroForm()
    if form.validate_on_submit():
        sucesso = send_user_registration_email(
            form.prontuario.data.strip(),
            form.nome.data.strip(),
            form.usuario.data.strip(),
            form.email.data.strip()
        )
        flash(
            "✅ Usuário cadastrado e e-mail enviado com sucesso!" if sucesso
            else "⚠️ Usuário cadastrado, mas falha no envio de e-mail.",
            "success" if sucesso else "warning"
        )
        return redirect(url_for("cadastro"))
    return render_template("cadastro.html", form=form)

# ---------- EXECUÇÃO ----------
if __name__ == '__main__':
    app.run(debug=True)