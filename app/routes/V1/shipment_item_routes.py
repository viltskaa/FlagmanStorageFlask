import jwt
import json
import flask
import pandas as pd
from flask import Response
from datetime import datetime, timedelta
from app.repositories import WorkerRepository
from app.services import ShipmentItemService, TokenService
from flask import Blueprint, jsonify, request, render_template
from app.utils.DisaiFileCacher.disai_file_casher import DisaiFileCasher
from flask import Blueprint, jsonify, request, g, render_template, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request

from werkzeug.exceptions import Unauthorized

shipment_item: flask.blueprints.Blueprint = Blueprint('shipment_item', __name__)

OPEN_ROUTES = {"/v1/shipment_item/list", "/v1/shipment_item/tokens"}


@shipment_item.errorhandler(jwt.InvalidTokenError)
def handle_invalid_token(error):
    return jsonify({"error": "Invalid token"}), 401


@shipment_item.errorhandler(Unauthorized)
def handle_unauthorized(error):
    return jsonify({"error": "Сессия обновлена"}), 401


@shipment_item.before_request
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


@shipment_item.route('', methods=['GET'])
@jwt_required()
def get_all():
    current_user_id = g.current_user["id"]
    items = ShipmentItemService.get_all(current_user_id)
    if items is None:
        return jsonify({
            "message": "Internal server error",
        }), 500
    item_list = [{
        'id': item.id,
        'article': item.article,
        'count_cur': item.count_cur,
        'count_all': item.count_all,
        'status': item.is_active,
        'for_this': item.for_this
    } for item in items]
    return jsonify(item_list)


@shipment_item.route('/shipment_product', methods=['POST'])
@jwt_required()
def product_shipment_add(dfc: DisaiFileCasher):
    data = request.get_json()

    if isinstance(data, list):
        return jsonify({
            "message": "Internal server error",
        }), 500

    gfc_entity = dfc.get_article(data.get('code'))
    if gfc_entity is None:
        return jsonify({
            "message": "Необходим код",
        }), 500

    ShipmentItemService.insert(gfc_entity.article, data.get('count_all'), datetime.now(), 'RECEIVED',
                               data.get('for_this'))
    return jsonify({
        "message": "shipment_item add success",
    }), 200


@shipment_item.route('/checkShipmentItems', methods=['GET'])
@jwt_required()
def check_shipment_items():
    current_user_id = g.current_user["id"]
    all_items_valid = ShipmentItemService.check_all_count_cur_equals_count_all(current_user_id)

    if all_items_valid:
        return jsonify({"status": "true"}), 200
    else:
        return jsonify({"status": "false"}), 200


@shipment_item.route('/scanQr', methods=['POST'])
@jwt_required()
def scan_qr(dfc: DisaiFileCasher):
    data = request.get_json()
    qrcode = data.get('qrcode')
    current_user_id = g.current_user["id"]
    if not qrcode:
        return jsonify({"message": "qrcode обязателен"}), 400

    qrcode_data = qrcode.split(",")
    gtin = qrcode_data[0][4:]

    gfc_entity = dfc.get_article(gtin)

    if gfc_entity is None:
        return jsonify({
            "message": "Article is't founded"
        }), 404
    article = gfc_entity.article

    success = ShipmentItemService.process_qr_scan(qrcode, article, current_user_id)

    if success:
        return jsonify({"message": "QR-код успешно обработан"}), 200
    else:
        return jsonify({"message": "Ошибка при обработке QR-кода"}), 400


@shipment_item.route('/<int:item_id>', methods=['POST'])
@jwt_required()
def outOfStock(item_id):
    current_user_id = g.current_user["id"]
    success, message = ShipmentItemService.handle_out_of_stock(item_id, current_user_id)
    print(message)
    if not success:
        status_code = 404 if message == "Item not found" else 500
        return jsonify({'error': message}), status_code

    return jsonify({'message': message}), 200


@shipment_item.route('/ship', methods=['POST'])
@jwt_required()
def shipping():
    current_user_id = g.current_user["id"]
    ship = ShipmentItemService.shipment_all(current_user_id)

    if ship:
        return jsonify({'message': 'Success shiping'}), 200
    else:
        return jsonify({"message": "Internal server error"}), 500


@shipment_item.route('/list', methods=['GET'])
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

        table = ShipmentItemService.get_all_by_period(datetime_start, datetime_end, status)
        print(table)
        dataframe = pd.DataFrame(table, columns=['article', 'count_cur', 'count_all', 'for_this', 'created_date',
                                                 'created_time'])

        dataframe.columns = ['Артикул', 'Отсканировано', 'Количество', 'Магазин', 'Дата', 'Время']

        return render_template(
            "ShipmentOrdersTable.html",
            table=dataframe.to_html(classes='table table-dark border rounded', justify='left', index=False)
        )

    return render_template("ShipmentOrdersTable.html", table="")


@shipment_item.route('/tokens', methods=['GET'])
def get_tokens():
    tokens = TokenService.get_tokens()
    if tokens is None:
        return jsonify({
            "message": "Internal server error",
        }), 500
    item_list = [{
        'id': item.id,
        'name': item.name,
    } for item in tokens]

    return Response(json.dumps(item_list, ensure_ascii=False), content_type="application/json; charset=utf-8")
