from flask import Blueprint

from .auth_routes import auth

V1_API_BLUEPRINT = Blueprint('v1', __name__)
V1_API_BLUEPRINT.register_blueprint(auth, url_prefix=f"/{auth.name}")
