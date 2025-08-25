from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)

# Página inicial
@app.route("/")
def index():
    return render_template("index.html", current_time=datetime.utcnow())

# Cumprimentar usuário
@app.route("/user/<name>")
def user(name):
    return render_template("user.html", name=name)

# Erro 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Executar
if __name__ == '__main__':
    app.run(debug=True)