import os
from datetime import timedelta
from pathlib import Path

from flask import Flask, redirect
from flask_injector import FlaskInjector
from injector import singleton

from config import DevelopConfig
from .database import database
from .routes import ROUTES
from .utils import pre, DisaiFileCasher

root_path = Path(__file__).parent.parent


def configure(binder):
    binder.bind(DisaiFileCasher, to=DisaiFileCasher(file=root_path / "data.csv"), scope=singleton)


def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopConfig)
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)

    for route in ROUTES:
        app.register_blueprint(route, url_prefix=f"/{route.name}")

    try:
        with app.app_context():
            database.init_app(app)
    except Exception as e:
        app.logger.error(e)

    @app.route('/')
    def storage():
        return redirect('/v1/item/list')

    if app.debug:
        @app.route('/routes')
        def route():
            return "<br/>".join([
                f"<a href={url.rule}>{url.endpoint}</a>" for url in app.url_map.iter_rules()
            ])

    FlaskInjector(app=app, modules=[configure])
    return app
