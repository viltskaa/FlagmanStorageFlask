from datetime import datetime, timedelta

import flask
import pandas as pd
from app.services import ShipmentItemService,ItemService
from app.repositories import ShipmentItemRepository
from flask import Blueprint, jsonify, request, g, render_template
from app.utils.DisaiFileCacher.disai_file_casher import DisaiFileCasher

shipment_item: flask.blueprints.Blueprint = Blueprint('shipment_item', __name__)


@shipment_item.route('/check',methods=['POST'])
def check_qr():
    data = request.get_json()
    qrcode = data.get('qrcode', None)
    if qrcode is None:
        return jsonify({
            "message": "Payload is empty"
        }), 400
    is_exist = ItemService.check_with_status(qrcode)
    if is_exist:
        return jsonify({"message": "QR code is valid"}), 200
    else:
        return jsonify({"message": "QR code not found"}), 400


@shipment_item.route('', methods=['GET'])
def get_all():
    items = ShipmentItemService.get_all()
    if items is None:
        return jsonify({
            "message": "Internal server error",
        }), 500
    item_list = [{
        'id': item.id,
        'article': item.article,
        'count_cur': item.count_cur,
        'count_all': item.count_all
    } for item in items]
    print(ShipmentItemRepository.last_error)
    return jsonify(item_list)


@shipment_item.route('/shipment_product', methods=['POST'])
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

    ShipmentItemService.insert(gfc_entity.article, data.get('count_all'),datetime.now())
    print(ShipmentItemRepository.last_error)
    return jsonify({
        "message": "shipment_item add success",
    }), 200

@shipment_item.route('/checkShipmentItems', methods=['GET'])
def check_shipment_items():
    all_items_valid = ShipmentItemService.check_all_count_cur_equals_count_all()

    if all_items_valid:
        return jsonify({"status": "true"}), 200
    else:
        return jsonify({"status": "false"}), 200


@shipment_item.route('/scanQr', methods=['POST'])
def scan_qr(dfc: DisaiFileCasher):
    data = request.get_json()
    qrcode = data.get('qrcode')

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

    success = ShipmentItemService.process_qr_scan(qrcode, article)

    if success:
        return jsonify({"message": "QR-код успешно обработан"}), 200
    else:
        return jsonify({"message": "Ошибка при обработке QR-кода"}), 400
