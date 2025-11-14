from flask import Flask

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
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config_object or 'flasky.config.Config')

    # Initialize extensions
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # register the main blueprint
    from .main import bp as main_bp
    app.register_blueprint(main_bp)

    # register auth blueprint (copied from aula.090)
    from .auth import auth as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Create alias endpoints without blueprint prefix for compatibility with existing templates
    # We postpone aliasing until after blueprint registration
    for rule in list(app.url_map.iter_rules()):
        if rule.endpoint.startswith(f"{main_bp.name}."):
            short_endpoint = rule.endpoint.split('.', 1)[1]
            view_func = app.view_functions.get(rule.endpoint)
            if short_endpoint not in app.view_functions:
                app.add_url_rule(rule.rule, endpoint=short_endpoint, view_func=view_func, methods=rule.methods)

    # import the errors module so it can register handlers
    from .main import errors  # noqa: F401

    # import models so they register with the app
    from . import models  # noqa: F401

    return app
