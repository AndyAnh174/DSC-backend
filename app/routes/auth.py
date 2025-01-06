from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_jwt
)
from ..models.user import User
from http import HTTPStatus

api = Namespace('auth', description='Xác thực người dùng')

# Lưu trữ các token đã bị vô hiệu hóa
blacklisted_tokens = set()

@api.route('/login')
class Login(Resource):
    def post(self):
        """Đăng nhập và lấy access token + refresh token"""
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return {
                    'message': 'Thiếu thông tin đăng nhập',
                    'error': 'MISSING_CREDENTIALS'
                }, HTTPStatus.BAD_REQUEST

            user = User.get_by_username(username)
            if not user or not user.check_password(password):
                return {
                    'message': 'Tên đăng nhập hoặc mật khẩu không đúng',
                    'error': 'INVALID_CREDENTIALS'
                }, HTTPStatus.UNAUTHORIZED

            # Tạo identity cho token
            identity = {
                'user_id': user.id,
                'username': user.username,
                'role': user.role
            }

            # Tạo access token và refresh token
            access_token = create_access_token(identity=identity)
            refresh_token = create_refresh_token(identity=identity)

            return {
                'message': 'Đăng nhập thành công',
                'data': {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'role': user.role
                    }
                }
            }, HTTPStatus.OK
        except Exception as e:
            return {
                'message': 'Lỗi khi đăng nhập',
                'error': str(e)
            }, HTTPStatus.INTERNAL_SERVER_ERROR

@api.route('/refresh')
class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        """Làm mới access token bằng refresh token"""
        try:
            current_user = get_jwt_identity()
            jti = get_jwt()['jti']
            
            # Kiểm tra xem refresh token có trong blacklist không
            if jti in blacklisted_tokens:
                return {
                    'message': 'Refresh token đã hết hạn hoặc bị vô hiệu hóa',
                    'error': 'INVALID_REFRESH_TOKEN'
                }, HTTPStatus.UNAUTHORIZED
            
            # Tạo access token mới
            new_access_token = create_access_token(identity=current_user)
            
            # Tạo refresh token mới (rotate refresh token)
            new_refresh_token = create_refresh_token(identity=current_user)
            
            # Thêm refresh token cũ vào blacklist
            blacklisted_tokens.add(jti)
            
            return {
                'message': 'Token đã được làm mới',
                'data': {
                    'access_token': new_access_token,
                    'refresh_token': new_refresh_token
                }
            }, HTTPStatus.OK
        except Exception as e:
            return {
                'message': 'Lỗi khi làm mới token',
                'error': str(e)
            }, HTTPStatus.INTERNAL_SERVER_ERROR

@api.route('/logout')
class Logout(Resource):
    @jwt_required()
    def post(self):
        """Đăng xuất và vô hiệu hóa token"""
        try:
            jti = get_jwt()['jti']
            blacklisted_tokens.add(jti)
            return {
                'message': 'Đăng xuất thành công'
            }, HTTPStatus.OK
        except Exception as e:
            return {
                'message': 'Lỗi khi đăng xuất',
                'error': str(e)
            }, HTTPStatus.INTERNAL_SERVER_ERROR 