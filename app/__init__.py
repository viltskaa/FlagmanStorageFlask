import os
from datetime import timedelta
from pathlib import Path

from flask import Flask, g, redirect

from config import DevelopConfig
from .database import database
from .routes import ROUTES
from .utils import pre, DisaiFileCasher


def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopConfig)
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)

    for route in ROUTES:
        app.register_blueprint(route, url_prefix=f"/{route.name}")

    try:
        database.init_app(app)

        @app.before_request
        def setup_dependencies():
            if 'disai_file_casher' in g:
                return

            print('init disai_file_casher')
            root_path = Path(__file__).parent.parent
            g.disai_file_casher = DisaiFileCasher(file=root_path / "data.csv")

    except Exception as e:
        app.logger.error(e)

    @app.route('/')
    def storage():
        return redirect('/v1/item/list')

    if app.debug:
        @app.route('/routes')
        def route():
            return pre("<br/>".join(
                [f"{url.endpoint:50} | {url.rule:20} | {url.methods}" for url in app.url_map.iter_rules()]
            ))

    return app
