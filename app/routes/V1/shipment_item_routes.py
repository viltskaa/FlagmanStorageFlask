from datetime import datetime, timedelta

import flask
import pandas as pd
from app.services import ShipmentItemService
from app.repositories import ShipmentItemRepository
from flask import Blueprint, jsonify, request, g, render_template
from app.utils.DisaiFileCacher.disai_file_casher import DisaiFileCasher

shipment_item: flask.blueprints.Blueprint = Blueprint('shipment_item', __name__)


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


@shipment_item.route('/updateByArticle', methods=['POST'])
def update_by_article(dfc: DisaiFileCasher):
    data = request.get_json()
    qrcode = data.get('code')
    flag = data.get('flag')
    if qrcode is None or flag is None:
        return jsonify({
            "message": "Invalid input. 'article' and 'flag' are required.",
        }), 500
    qrcode_data = qrcode.split(",")
    gtin = qrcode_data[0][4:]

    gfc_entity = dfc.get_article(gtin)

    if gfc_entity is None:
        return jsonify({
            "message": "Article is't founded"
        }), 404
    article = gfc_entity.article
    order = ShipmentItemService.get_by_article(article)

    if order is None:
        return jsonify({'error': f'Order with article {article} not found'}), 404
    if order.is_active == 1:
        return jsonify({'error': f'Order with article {article} not found in no shipment items'}), 404
    new_count_cur = 0
    if flag == "true":
        if order.count_cur < order.count_all:
            new_count_cur = order.count_cur + 1
        else:
            return jsonify({'error': f'Cannot increase count_cur for article {article} beyond count_all'}), 400
    if flag == "false":
        if order.count_cur > 0:
            new_count_cur = order.count_cur - 1
        else:
            return jsonify({'error': f'Cannot reduce count_cur for article {article} below zero'}), 400

    if not ShipmentItemService.update_count_cur(order.id, new_count_cur):
        return jsonify({
            'error': 'Failed to update count_cur in the database'
        }), 500

    return jsonify({'message': 'Article updated successfully'}), 200

@shipment_item.route('/checkShipmentItems', methods=['GET'])
def check_shipment_items():
    all_items_valid = ShipmentItemService.check_all_count_cur_equals_count_all()

    if all_items_valid:
        return jsonify({"status": "true"}), 200
    else:
        return jsonify({"status": "false"}), 200

@shipment_item.route('/ship', methods=['POST'])
def shiping():
    ship = ShipmentItemService.update_today_is_active()

    if ship:
        return jsonify({'message': 'Success shiping'}), 200
    else:
        return jsonify({"message": "Internal server error"}), 500

@shipment_item.route('/<int:item_id>', methods=['POST'])
def outOfStock(item_id):
    print(item_id)
    shipment = ShipmentItemService.get_by_id(item_id)
    if shipment is None:
        return jsonify({
            'error': 'Item not found'
        }),404
    tomorrow = datetime.now() + timedelta(days=1)
    if not ShipmentItemService.insert(shipment.article, shipment.count_all-shipment.count_cur, tomorrow):
        return jsonify({
            'error': 'Failed to insert new Item in the database'
        }), 500
    if shipment.count_cur == 0:
        if not ShipmentItemService.delete_by_id(item_id):
            return jsonify({
                'error': 'Failed to delete Item in the database'
            }), 500
    else:
        if not ShipmentItemService.update_count_all(item_id, shipment.count_cur):
            return jsonify({
                'error': 'Failed to update Item in the database'
            }), 500
    return jsonify({'message': 'Success'}), 200


@shipment_item.route('/list', methods=['GET'])
def get_storage():
    table = ShipmentItemService.get_all()
    dataframe = pd.DataFrame(table, columns=['id', 'article', 'count_cur', 'count_all'])
    dataframe = dataframe.drop(columns=['id'])
    dataframe.columns = ['Артикул', 'Количество отсканировано', 'Количество всего']

    return render_template(
        "StorageTable.html",
        table=dataframe.to_html(classes='table table-dark border rounded', justify='left', index=False),
    )
