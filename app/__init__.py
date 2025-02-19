import os
from datetime import timedelta
from pathlib import Path
import atexit
from flask_jwt_extended import JWTManager
import click
from flask import Flask, redirect
from flask_injector import FlaskInjector
from injector import singleton
from apscheduler.schedulers.background import BackgroundScheduler

from config import DevelopConfig
from .database import database
from .routes import ROUTES
from .utils import pre, DisaiFileCasher
from app.services.wb_service import WBService

root_path = Path(__file__).parent.parent


def configure(binder):
    binder.bind(DisaiFileCasher, to=DisaiFileCasher(file=root_path / "data.csv"), scope=singleton)


def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopConfig)
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

    jwt = JWTManager(app)

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

    scheduler = BackgroundScheduler()

    def fetch_all():
        with app.app_context():
            try:
                WBService.fetch_orders('АЛИСА2')
                WBService.fetch_orders('СЕВЕРНОЕ')
            except Exception as e:
                app.logger.error(f"Scheduler error: {e}")

    scheduler.add_job(fetch_all, 'cron', hour=8, minute=00)
    scheduler.start()

    @click.command("manual-parse")
    def manual_parse():
        fetch_all()
        app.logger.info("parse complete")

    app.cli.add_command(manual_parse)

    atexit.register(lambda: scheduler.shutdown())

    return app
