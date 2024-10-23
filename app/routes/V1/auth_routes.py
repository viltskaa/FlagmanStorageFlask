import flask
from flask import Blueprint, Response, request, current_app, json

from app.services import AuthorizationService

auth: flask.blueprints.Blueprint = Blueprint('auth', __name__)


@auth.route('/register', methods=['POST'])
def register() -> Response:
    data = request.json
    name = data.get('name', None)
    surname = data.get('surname', None)
    patronymic = data.get('patronymic', None)
    password = data.get('password', None)

    if not all([name, surname, password]):
        return current_app.response_class(
            response=json.dumps({'error': 'No params provided'}),
            status=400,
            mimetype='application/json'
        )

    w_id = AuthorizationService.register(name, surname, patronymic, password)

    if w_id:
        return current_app.response_class(
            response=json.dumps({"msg": "Worker registered successfully",
                                 "worker_id": w_id}),
            status=200,
            mimetype='application/json'
        )
    else:
        return current_app.response_class(
            response=json.dumps({'error': 'An error occurred during register'}),
            status=500,
            mimetype='application/json'
        )


@auth.route('/login', methods=['POST'])
def login() -> Response:
    data = request.json
    name = data.get("name", None)
    surname = data.get("surname", None)
    patronymic = data.get("patronymic", None)
    password = data.get("password", None)

    token = AuthorizationService.login(name, surname, patronymic, password)

    if token:
        return current_app.response_class(
            response=json.dumps({"msg": "Successfully logged in",
                                 "token": token}),
            status=200,
            mimetype='application/json'
        )
    else:
        return current_app.response_class(
            response=json.dumps({'error': 'An error occurred during login'}),
            status=500,
            mimetype='application/json'
        )
