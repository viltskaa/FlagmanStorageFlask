import ast

import jwt
import json
import flask
import pandas as pd
import requests
from flask import Response
from datetime import datetime, timedelta
from app.repositories import WorkerRepository
from app.services import ShipmentItemService, TokenService, WBService
from app.utils.DisaiFileCacher.disai_file_casher import DisaiFileCasher
from flask import Blueprint, jsonify, request, g, render_template, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request

from werkzeug.exceptions import Unauthorized

shipment_item: flask.blueprints.Blueprint = Blueprint('shipment_item', __name__)

OPEN_ROUTES = {"/v1/shipment_item/list", "/v1/shipment_item/tokens"}
PRINTER_URL = 'http://192.168.172.149:8000/print'
@shipment_item.route('/scanQrOnPalet', methods=['POST'])
@jwt_required()
def scan_qr_pallet():
    data = request.get_json()
    qrcode = data.get('qrcode')

    if not qrcode:
        return jsonify({"message": "qrcode обязателен"}), 400
    status = ShipmentItemService.check_is_shipment(qrcode)
    if not status:
        return jsonify({"message": "продукт еще не отгружен"}), 400
    order = ShipmentItemService.get_order_by_qrcode(qrcode)
    sticker = WBService.get_sticker(order)
    if sticker is None:
        return jsonify({"message": "Нет стикера"}), 400
    file=sticker.get('file',"")
    response = None
    try:
        body = {
            "image": file
        }
        response = requests.post(PRINTER_URL, json=body)
        response.raise_for_status()
        data = response.json()
        return jsonify({"message": data.get("message")}), 200
    except requests.exceptions.HTTPError as http_err:
        error_message = f"HTTP error occurred: {http_err}"
        if response is not None:
            error_message += f" - Response: {response.text}"
        print(error_message)
        return jsonify({
            "message": error_message
        }), 500

    except Exception as err:
        print(err)
        return jsonify({
            "message": f"An error occurred: {err}"
        }), 500



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
    grouped_items = ShipmentItemService.get_all(current_user_id)
    if grouped_items is None:
        return jsonify({
            "message": "Internal server error",
        }), 500
    print(grouped_items)
    return jsonify(grouped_items)


@shipment_item.route('/toShipment', methods=['GET'])
@jwt_required()
def get_all_shipment():
    current_user_id = g.current_user["id"]
    grouped_items = ShipmentItemService.get_all_to_ship(current_user_id)
    if grouped_items is None:
        return jsonify({
            "message": "Internal server error",
        }), 500
    print(grouped_items)
    return jsonify(grouped_items)

@shipment_item.route('/checkShipmentItems', methods=['GET'])
@jwt_required()
def check_shipment_items():
    current_user_id = g.current_user["id"]
    all_items_valid = ShipmentItemService.check_all_fully_scanned(current_user_id)
    if all_items_valid:
        return jsonify({"status": "true"}), 200
    else:
        return jsonify({"status": "false"}), 200


@shipment_item.route('/checkShipmentItemsToShip', methods=['GET'])
@jwt_required()
def check_shipment_items_to_ship():
    current_user_id = g.current_user["id"]
    all_items_valid = ShipmentItemService.check_all_fully_to_ship_scanned(current_user_id)

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

    success = ShipmentItemService.process_qr_scan(qrcode, article, current_user_id,"STORAGE")

    if success:
        return jsonify({"message": "QR-код успешно обработан"}), 200
    else:
        return jsonify({"message": "Ошибка при обработке QR-кода"}), 400


@shipment_item.route('/scanQrToShip', methods=['POST'])
@jwt_required()
def scan_qr_to_ship(dfc: DisaiFileCasher):
    data = request.get_json()
    qrcode = data.get('qrcode')
    current_user_id = g.current_user["id"]

    if not qrcode:
        return jsonify({"message": "qrcode обязателен"}), 400

    gtin = qrcode.split(",")[0][4:]
    gfc_entity = dfc.get_article(gtin)

    if gfc_entity is None:
        return jsonify({"message": "Article isn't found"}), 404

    article = gfc_entity.article

    if not ShipmentItemService.process_qr_to_ship(qrcode, article, current_user_id, "TO_SHIP"):
        return jsonify({"message": "Ошибка при обработке QR-кода"}), 400

    order = ShipmentItemService.get_order_by_qrcode(qrcode)
    sticker = WBService.get_sticker(order)

    if not sticker:
        return jsonify({"message": "Нет стикера"}), 400

    file = sticker.get('file', "")

    try:
        response = requests.post(PRINTER_URL, json={"image": file})
        response.raise_for_status()
        return jsonify({"message": response.json().get("message")}), 200
    except requests.exceptions.RequestException as err:
        return jsonify({"message": f"Ошибка при отправке на принтер: {err}"}), 500


@shipment_item.route('/outOfStock', methods=['POST'])
@jwt_required()
def outOfStock():
    data = request.get_json()
    full_name = data.get('full_name')
    print(full_name)
    orderUid = data.get('orderUid')
    success, message = ShipmentItemService.handle_out_of_stock(orderUid, full_name)
    if not success:
        status_code = 404 if message == "Такого пользователя нет" else 500
        return jsonify({'error': message}), status_code
    return jsonify({'message': message}), 200


@shipment_item.route('/to_ship', methods=['POST'])
@jwt_required()
def to_shipping():
    current_user_id = g.current_user["id"]
    ship = ShipmentItemService.to_shipment_all(current_user_id)

    if ship:
        return jsonify({'message': 'Success to ship'}), 200
    else:
        return jsonify({"message": "Internal server error"}), 500


@shipment_item.route('/shipmentAll', methods=['POST'])
@jwt_required()
def shipped():
    current_user_id = g.current_user["id"]

    unique_supply_ids, success = ShipmentItemService.shipped_all(current_user_id)
    print(unique_supply_ids)
    if not success:
        return jsonify({"message": "Internal server error"}), 500

    #for supply_id in unique_supply_ids:
        #qr_code = WBService.get_supply_qr(supply_id)
        #if not qr_code:
            #return jsonify({"message": f"Не удалось получить QR-код для supply_id {supply_id}"}), 400
        #file = qr_code.get('file', "")
        #try:
            #response = requests.post(PRINTER_URL, json={"image": file})
           # response.raise_for_status()

        #except requests.exceptions.HTTPError as http_err:
            #error_message = f"HTTP error occurred: {http_err}"
           # return jsonify({"message": error_message, "supply_id": supply_id}), 500
        #except Exception as err:
           # return jsonify({"message": f"An error occurred: {err}", "supply_id": supply_id}), 500

    return jsonify({'message': 'Success shipping', 'supply_ids': unique_supply_ids}), 200



@shipment_item.route('/cancel/<string:orderUid>', methods=['POST'])
@jwt_required()
def cancel(orderUid):
    remove_from_shipment = request.json.get('remove_from_shipment', True)
    ship = ShipmentItemService.cancel(orderUid=orderUid, remove_from_shipment=remove_from_shipment)
    if ship:
        return jsonify({'message': 'Success cancel'}), 200
    else:
        return jsonify({'message': 'Internal server error'}), 500



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
        dataframe = pd.DataFrame(table, columns=['article', 'orderUid', 'action_time', 'for_this', 'created_date',
                                                 'created_time'])

        dataframe.columns = ['Артикул', 'Заказ', 'Время(если None - поступили)', 'Магазин', 'Дата', 'Время']

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
