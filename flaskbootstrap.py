from flask import Flask, render_template
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from wtforms import StringField, SubmitField
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
    submit = SubmitField('Enviar')

@app.route('/forms', methods=['GET', 'POST'])
def forms():
    form = NomeForm()
    nome = 'Stranger'
    if form.validate_on_submit():
        nome = form.nome.data
    return render_template('forms.html', form=form, nome=nome)

# Executar
if __name__ == '__main__':
    app.run(debug=True)
