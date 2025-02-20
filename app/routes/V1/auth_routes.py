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
    tokens = data.get('tokens',None)
    if not all([name, surname,patronymic,password,tokens]):
        return current_app.response_class(
            response=json.dumps({'error': 'No params provided'}),
            status=400,
            mimetype='application/json'
        )
    w_id = AuthorizationService.register(name, surname, patronymic,password,tokens)

    if w_id:
        return current_app.response_class(
            response=json.dumps({"msg": "Worker registered successfully", "worker_id": w_id}),
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
    qrcode = data.get('qrcode')
    qrcode_data = qrcode.split(",")
    print(qrcode)
    surname = qrcode_data[1][7:]
    name = qrcode_data[0][4:]
    patronymic = qrcode_data[2][10:]
    password = qrcode_data[3][8:]
    token = AuthorizationService.login(name, surname, patronymic,password)

    if token:
        return current_app.response_class(
            response=json.dumps({"msg": "Successfully logged in", "token": token}),
            status=200,
            mimetype='application/json'
        )
    else:
        return current_app.response_class(
            response=json.dumps({'error': 'An error occurred during login'}),
            status=500,
            mimetype='application/json'
        )

@auth.route('/refresh',methods=['POST'])
def refresh() -> Response:
    data = request.json
    name = data.get("name", None)
    surname = data.get("surname", None)
    patronymic = data.get("patronymic", None)
    token = AuthorizationService.refresh(name,surname,patronymic)
    if token:
        return current_app.response_class(
            response=json.dumps({"msg": "Обновленная сессия", "token": token}),
            status=200,
            mimetype='application/json'
        )
    else:
        return current_app.response_class(
            response=json.dumps({'error': 'Ошибка при обновлении'}),
            status=500,
            mimetype='application/json'
        )

