from flask_restful import Api, Resource, marshal_with, fields
from sqlalchemy.ext.hybrid import hybrid_property
from flask_security import auth_required, hash_password, verify_password, roles_required
from flask import current_app as app, request, jsonify, make_response
from backend.models import *
import time

api = Api(prefix='/api')

# Define fields for userDetails
userDetail_fields = {
    'id': fields.Integer,
    'user_id': fields.Integer,
    'first_name': fields.String,
    'last_name': fields.String,
    'dob': fields.String,
    'bio': fields.String,
    'gender': fields.String,
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime,
}

class UserDetailApi(Resource):
    @marshal_with(userDetail_fields)
    @auth_required()
    def get(self, userId):
        try:
            userDetail = UserDetail.query.filter_by(user_id=userId).first_or_404()
        except Exception as e:
            return make_response(jsonify({
                "status": "error",
                "message": f"userDetail with userId {userId} not found.",
                "details": str(e)
            }), 404)
        time.sleep(2)
        return userDetail 
api.add_resource(UserDetailApi, '/user/<int:userId>')