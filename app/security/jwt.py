from flask import jsonify
from flask_jwt_extended import get_jwt
from app.extensions import jwt, db
from app.db.models.token_blocklist import TokenBlocklist

def init_jwt(app):
    jwt.init_app(app)

    @jwt.token_in_blocklist_loader
    def token_in_blocklist_loader(_jwt_header, jwt_payload):
        jti = jwt_payload.get("jti")
        if not jti:
            return False
        row = db.session.query(TokenBlocklist).filter_by(jti=jti).first()
        return row is not None

    @jwt.revoked_token_loader
    def revoked_token_loader(_jwt_header, _jwt_payload):
        return jsonify({"error": "token_revoked"}), 401

    @jwt.unauthorized_loader
    def unauthorized_loader(_msg):
        return jsonify({"error": "missing_token"}), 401

    @jwt.invalid_token_loader
    def invalid_token_loader(_msg):
        return jsonify({"error": "invalid_token"}), 401

    @jwt.expired_token_loader
    def expired_token_loader(_jwt_header, _jwt_payload):
        return jsonify({"error": "token_expired"}), 401
