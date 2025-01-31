import flask
import pandas as pd
from flask import Blueprint, jsonify, request, g, render_template

from app.services import ItemService
from app.utils.DisaiFileCacher.disai_file_casher import DisaiFileCasher

item: flask.blueprints.Blueprint = Blueprint('item', __name__)


@item.route('/product', methods=['POST'])
def product_add(dfc: DisaiFileCasher):
    data = request.get_json()

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

        ItemService.insert(gfc_entity.article, qrocde)

    return jsonify({
        "message": "List of scanned items processed successfully",
    }), 200


@item.route('/write_off', methods=['POST'])
def write_off():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({
            "message": "Internal server error",
        }), 500

    for row in data:
        qrocde = row.get('code', None)

        if qrocde is None:
            continue

        ItemService.write_off(qrocde)

    return jsonify({
        "message": "List of scanned items processed successfully",
    }), 200


@item.route('/unique', methods=['POST'])
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
    table = ItemService.get_all()
    dataframe = pd.DataFrame(table, columns=['id', 'article', 'qrcode'])
    dataframe = dataframe[['article']].value_counts().reset_index(name='Count')
    dataframe.columns = ['Артикул', 'Количество']

    return render_template(
        "StorageTable.html",
        table=dataframe.to_html(classes='table table-dark border rounded', justify='left', index=False),
    )
