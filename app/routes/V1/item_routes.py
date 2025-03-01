from datetime import datetime
from flask_jwt_extended import jwt_required,get_jwt_identity,verify_jwt_in_request
import flask
import pandas as pd
from flask import Blueprint, jsonify, request, g, render_template,abort
from app.repositories import WorkerRepository
from app.services import ItemService
from app.utils.DisaiFileCacher.disai_file_casher import DisaiFileCasher

item: flask.blueprints.Blueprint = Blueprint('item', __name__)
import jwt
from werkzeug.exceptions import Unauthorized

OPEN_ROUTES = {"/v1/item/list"}

@item.errorhandler(jwt.InvalidTokenError)
def handle_invalid_token(error):
    return jsonify({"error": "Invalid token"}), 401

@item.errorhandler(Unauthorized)
def handle_unauthorized(error):
    return jsonify({"error": "Сессия обновлена"}), 401

@item.before_request
def load_current_user():
    if request.path in OPEN_ROUTES:
        return
    try:
        verify_jwt_in_request()
        current_user = get_jwt_identity()
        current_user = WorkerRepository.get_by_full_name(current_user)
        if not current_user:
            abort(401, description="Unauthorized: User not found")
        g.current_user = current_user
    except Exception:
        abort(401, description="Unauthorized")

@item.route('/product', methods=['POST'])
@jwt_required()
def product_add(dfc: DisaiFileCasher):
    data = request.get_json()
    current_user_id = g.current_user["id"]
    if not isinstance(data, list):
        return jsonify({
            "message": "Internal server error",
        }), 500

    for row in data:
        qrocde = row.get('code', None)

        if qrocde is None:
            continue

        qrcode_data = qrocde.split(",")
        gtin = qrcode_data[0][4:]

        gfc_entity = dfc.get_article(gtin)
        if gfc_entity is None:
            continue

        ItemService.insert(gfc_entity.article, qrocde, current_user_id)

    return jsonify({
        "message": "List of scanned items processed successfully",
    }), 200


@item.route('/check_storage', methods=['POST'])
def check_storage():
    try:
        data = request.get_json()
        qrcode = data.get('code')

        if not qrcode:
            return jsonify({"error": "QR code is required"}), 400

        exists = ItemService.check(qrcode)
        if exists:
            return jsonify({"exists": "true"}), 200
        else:
            return jsonify({"exists": "false"}), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@item.route('/check_write_off',methods=['POST'])
def check_write_off():
    try:
        data = request.get_json()
        qrcode = data.get('code')

        if not qrcode:
            return jsonify({"error": "QR code is required"}), 400
        exists = ItemService.check_with_status_write_off(qrcode)
        if exists:
            return jsonify({"exists": "true"}), 200
        else:
            return jsonify({"exists": "false"}), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500



@item.route('/write_off', methods=['POST'])
@jwt_required()
def write_off():
    data = request.get_json()
    current_user_id = g.current_user["id"]
    if not isinstance(data, list):
        return jsonify({
            "message": "Internal server error",
        }), 500

    for row in data:
        qrcode = row.get('code', None)

        if qrcode is None:
            continue

        ItemService.write_off(qrcode,current_user_id)

    return jsonify({
        "message": "List of scanned items processed successfully",
    }), 200


@item.route('/refund', methods=['POST'])
@jwt_required()
def refund():
    data = request.get_json()
    current_user_id = g.current_user["id"]
    if not isinstance(data, list):
        return jsonify({
            "message": "Internal server error",
        }), 500

    for row in data:
        qrcode = row.get('code', None)

        if qrcode is None:
            continue

        ItemService.refund(qrcode,current_user_id)

    return jsonify({
        "message": "List of scanned items processed successfully",
    }), 200


@item.route('/unique', methods=['POST'])
@jwt_required()
def get_article_and_check_unique(dfc: DisaiFileCasher):
    data = request.get_json()

    qrcode = data.get('qrcode', None)
    gtin = data.get('gtin', None)
    if qrcode is None or gtin is None:
        return jsonify({
            "message": "Payload is empty"
        }), 400

    is_exist = ItemService.check(qrcode)
    if is_exist:
        return jsonify({
            "message": "qrcode already exists",
        }), 205

    article = dfc.get_article(gtin)
    if article is None:
        return jsonify({
            "message": "Article is't founded"
        }), 404

    return jsonify(article), 200


@item.route('/list', methods=['GET'])
def get_storage():
    date_start = request.args.get('dateStart')
    date_end = request.args.get('dateEnd')
    status = request.args.get('status')
    if date_start and date_end:
        try:
            datetime_start = datetime.strptime(date_start, "%Y-%m-%dT%H:%M")
            datetime_end = datetime.strptime(date_end, "%Y-%m-%dT%H:%M")
        except ValueError:
            return "Неверный формат даты", 400

        table = ItemService.get_all_by_period(datetime_start, datetime_end, status)
    else:
        table = ItemService.get_all()
    dataframe = pd.DataFrame(table, columns=['id', 'article', 'qrcode'])
    dataframe = dataframe[['article']].value_counts().reset_index(name='Count')
    dataframe.columns = ['Артикул', 'Количество']

    return render_template(
        "StorageTable.html",
        table=dataframe.to_html(classes='table table-dark border rounded', justify='left', index=False)
    )

    return render_template("StorageTable.html", table="")
