from app.services import TokenService
import flask
from flask import Blueprint, request, current_app, render_template,json

token: flask.blueprints.Blueprint = Blueprint('token', __name__)


@token.route('/insert', methods=['POST', 'GET'])
def insert():
    if request.method == 'POST':
        data = request.json
        name = data.get('name', None)
        token_value = data.get('token', None)

        if not all([name, token_value]):
            return current_app.response_class(
                response=json.dumps({'error': 'No params provided'}),
                status=400,
                mimetype='application/json'
            )

        t_id = TokenService.insert(name, token_value)
        if t_id:
            return current_app.response_class(
                response=json.dumps({"msg": "token inserted successfully", "token_id": t_id}),
                status=200,
                mimetype='application/json'
            )
        else:
            return current_app.response_class(
                response=json.dumps({'error': 'An error occurred during insert'}),
                status=500,
                mimetype='application/json'
            )

    elif request.method == 'GET':
        return render_template('token.html')
