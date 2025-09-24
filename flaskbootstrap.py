from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)

app.config['SECRET_KEY'] = 'zovedi123'

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

# Formulário
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
class LoginForm(FlaskForm):
    usuario = StringField('Usuário ou E-mail', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

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

@app.route("/listausuario", methods=["GET", "POST"])
def listausuario():
    nome = None
    if request.method == "POST":
        nome = request.form.get("nome")
        if nome:
            # usamos a lista global 'usuarios'
            usuarios.append({"nome": nome, "funcao": "User"})
    return render_template("listausuario.html", nome=nome, usuarios=usuarios)

# Lista global de usuários
usuarios = [
    {"nome": "Lucca", "funcao": "Administrator"},
    {"nome": "Zovedi", "funcao": "User"},
]


# Executar
if __name__ == '__main__':
    app.run(debug=True)
