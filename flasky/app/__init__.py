from flask import Flask
import os

# Optional dependency shim: if an extension isn't installed we provide a
# lightweight object with an `init_app` method so the package can be
# imported in minimal environments (useful for static analysis or tests
# that don't require the full runtime stack).
class _ShimExt:
    def init_app(self, app):
        return None

try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv():
        return None

try:
    from flask_bootstrap import Bootstrap
except Exception:
    Bootstrap = _ShimExt

try:
    from flask_moment import Moment
except Exception:
    Moment = _ShimExt

try:
    from flask_sqlalchemy import SQLAlchemy
except Exception:
    SQLAlchemy = _ShimExt

try:
    from flask_login import LoginManager
except Exception:
    LoginManager = _ShimExt

try:
    from flask_mail import Mail
except Exception:
    Mail = _ShimExt

load_dotenv()

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
try:
    login_manager.login_view = 'auth.login'
except Exception:
    pass
mail = Mail()


def create_app(config_object=None):
    """Application factory (simplified).

    Only initializes what is needed for the index and disciplina routes.
    """
    app = Flask(__name__)
    app.config.from_object(config_object or 'flasky.config.Config')

    # Ensure a SECRET_KEY exists so Flask-WTF CSRF can operate.
    # In production set a strong secret via environment variable `SECRET_KEY`.
    if not app.config.get('SECRET_KEY'):
        # fallback to environment or a development default
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret'
        print('Warning: SECRET_KEY not set in config; using insecure development default.', flush=True)
    # Ensure WTF_CSRF_SECRET_KEY is set (Flask-WTF uses it if present)
    app.config.setdefault('WTF_CSRF_SECRET_KEY', app.config['SECRET_KEY'])

    # Initialize only the extensions we need for the two pages
    try:
        bootstrap.init_app(app)
    except Exception:
        pass
    moment.init_app(app)
    db.init_app(app)

    # simple routes: index (uses moment) and disciplina
    from flask import render_template
    from datetime import datetime

    @app.route('/')
    def index():
        return render_template('index.html', current_time=datetime.utcnow())

    from flask import request, redirect, url_for, flash
    from .models import Discipline

    @app.route('/disciplina', methods=['GET', 'POST'])
    def disciplina():
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            semester = request.form.get('semester', '').strip()
            # basic validation
            if not name or not semester:
                flash('Por favor informe o nome da disciplina e selecione o semestre.', 'danger')
                return redirect(url_for('disciplina'))
            try:
                sem_int = int(semester)
            except ValueError:
                sem_int = None
            if sem_int is None or sem_int < 1 or sem_int > 6:
                flash('Semestre inválido. Escolha um valor entre 1 e 6.', 'danger')
                return redirect(url_for('disciplina'))

            # save to database
            disc = Discipline(name=name, semester=sem_int)
            try:
                db.session.add(disc)
                db.session.commit()
            except Exception:
                db.session.rollback()
                flash('Erro ao salvar no banco de dados.', 'danger')
                return redirect(url_for('disciplina'))

            flash(f'Disciplina "{name}" cadastrada no semestre {sem_int}.', 'success')
            return redirect(url_for('disciplina'))

        # query persisted disciplines
        disciplines = Discipline.query.order_by(Discipline.id.desc()).all()
        return render_template('disciplina.html', disciplines=disciplines)

    @app.errorhandler(404)
    def page_not_found(e):
        from flask import render_template
        return render_template('404.html'), 404

    return app
