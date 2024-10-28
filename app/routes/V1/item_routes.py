import flask
from flask import Blueprint, Response, jsonify, request, current_app, json

from app.services import ItemService

item: flask.blueprints.Blueprint = Blueprint('item', __name__)

@item.route('/orders', methods=['GET'])
def orders():
    # Получаем заказы и сохраняем их в базу данных
    boolean = request.args.get('load')

    # Если параметр load равен "true", загружаем заказы
    if boolean == "true":
        ItemService.get_wildberries_orders()
    print(boolean)
    # Получаем все записи из таблицы Item
    items = ItemService.get_all()

    # Преобразуем объекты Item в список словарей для JSON-ответа
    item_list = [{
        'id': item.id,
        'article': item.article,
        'count': item.count
    } for item in items]

    # Возвращаем JSON-ответ с данными
    return jsonify(item_list)


@item.route('/product_introduction', methods=['POST'])
def product_introduction():
    data = request.get_json()

    if isinstance(data, list):
        scanned_items = data
        print(f"Received scanned items: {scanned_items}")
        return jsonify({"message": "List of scanned items received", "items": scanned_items}), 200
    else:
        return jsonify({"error": "Invalid input, expected a list of items"}), 400


@item.route('/orders/updateByArticle', methods=['POST'])
def update_by_article():
    data = request.get_json()

    article = data
    order = ItemService.get_by_article(article)

    if order is None:
        return jsonify({'error': 'Order not found'}), 404

    if order.count > 0:
        order.count -= 1  # Уменьшаем количество
        if order.count == 0:
            ItemService.delete_by_id(order.id)# Удаляем запись, если count стал 0
    else:
        return jsonify({'error': 'Cannot reduce count below zero'}), 400  # Дополнительная проверка

    return jsonify({'message': 'Article updated successfully'}), 200
