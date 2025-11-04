from flask import Flask
from dotenv import load_dotenv
import os

# Extensions are optional for import-time resilience. If packages are missing, we create
# small shim objects with an init_app method so create_app can still be imported in
# environments without all dependencies installed.
class _ShimExt:
    def init_app(self, app):
        return None

try:
    from flask_bootstrap import Bootstrap
except Exception:
    Bootstrap = _ShimExt

try:
    from flask_moment import Moment
except Exception:
    Moment = _ShimExt

bootstrap = Bootstrap()
moment = Moment()


def create_app(config_object=None):
    """Application factory."""
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(config_object or 'flasky.config.Config')

    bootstrap.init_app(app)
    moment.init_app(app)

    # register the main blueprint
    from .main import bp as main_bp
    app.register_blueprint(main_bp)

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

    # import models (placeholder)
    from . import models  # noqa: F401

    return app
