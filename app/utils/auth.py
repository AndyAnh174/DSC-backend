from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from http import HTTPStatus

def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return {
                'message': 'Token không hợp lệ hoặc đã hết hạn',
                'error': str(e)
            }, HTTPStatus.UNAUTHORIZED
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user = get_jwt_identity()
            if current_user.get('role') != 'admin':
                return {
                    'message': 'Bạn không có quyền thực hiện hành động này',
                    'error': 'PERMISSION_DENIED'
                }, HTTPStatus.FORBIDDEN
            return fn(*args, **kwargs)
        except Exception as e:
            return {
                'message': 'Token không hợp lệ hoặc đã hết hạn',
                'error': str(e)
            }, HTTPStatus.UNAUTHORIZED
    return wrapper 