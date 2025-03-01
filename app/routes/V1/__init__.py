from flask import Blueprint
from .worker_routes import worker
from .auth_routes import auth
from .item_routes import item
from .shipment_item_routes import shipment_item
from .token_routes import token


V1_API_BLUEPRINT = Blueprint('v1', __name__)
V1_API_BLUEPRINT.register_blueprint(auth, url_prefix=f"/{auth.name}")
V1_API_BLUEPRINT.register_blueprint(item, url_prefix=f"/{item.name}")
V1_API_BLUEPRINT.register_blueprint(worker, url_prefix=f"/{worker.name}")
V1_API_BLUEPRINT.register_blueprint(shipment_item, url_prefix=f"/{shipment_item.name}")
V1_API_BLUEPRINT.register_blueprint(token, url_prefix=f"/{token.name}")