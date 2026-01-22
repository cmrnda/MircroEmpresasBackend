from flask_jwt_extended import get_jwt
from app.extensions import jwt
from app.extensions import db
from app.database.models.token_blocklist import TokenBlocklist

def init_jwt():
    @jwt.token_in_blocklist_loader
    def _token_in_blocklist_loader(jwt_header, jwt_payload):
        jti = jwt_payload.get("jti")
        if not jti:
            return True
        row = db.session.query(TokenBlocklist).filter(TokenBlocklist.jti == str(jti)).first()
        return row is not None

    @jwt.revoked_token_loader
    def _revoked(jwt_header, jwt_payload):
        return {"error": "token_revoked"}, 401

    @jwt.expired_token_loader
    def _expired(jwt_header, jwt_payload):
        return {"error": "token_expired"}, 401

    @jwt.invalid_token_loader
    def _invalid(msg):
        return {"error": "token_invalid"}, 401

    @jwt.unauthorized_loader
    def _missing(msg):
        return {"error": "token_missing"}, 401
