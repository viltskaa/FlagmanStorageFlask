import flask

from .V1 import V1_API_BLUEPRINT

ROUTES: list[flask.blueprints.Blueprint] = [
    V1_API_BLUEPRINT,
]
