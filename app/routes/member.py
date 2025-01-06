from flask import request, jsonify, make_response
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.member import Member
from http import HTTPStatus
import os
from werkzeug.utils import secure_filename
from flask import current_app, url_for
import time
import traceback

api = Namespace('members', description='Quản lý thành viên')

# Định nghĩa model cho API documentation
links_model = api.model('Links', {
    'facebook': fields.String(required=True),
    'github': fields.String(required=True),
    'email': fields.String(required=True)
})

member_model = api.model('Member', {
    'name': fields.String(required=True),
    'role': fields.String(required=True),
    'avatar': fields.String(required=True),
    'team': fields.String(required=True),
    'department': fields.String(required=True),
    'year': fields.String(required=False),
    'skills': fields.List(fields.String, required=True),
    'links': fields.Nested(links_model)
})

@api.route('/')
class MemberList(Resource):
    @api.doc('list_members')
    def get(self):
        """Lấy danh sách tất cả thành viên"""
        try:
            members = Member.get_all()
            return {
                'message': 'Lấy danh sách thành viên thành công',
                'data': [member.__dict__ for member in members]
            }, HTTPStatus.OK
        except Exception as e:
            return {
                'message': 'Lỗi khi lấy danh sách thành viên',
                'error': str(e)
            }, HTTPStatus.INTERNAL_SERVER_ERROR

    @api.doc('create_member')
    @api.expect(member_model)
    @jwt_required()
    def post(self):
        """Tạo thành viên mới"""
        try:
            data = request.get_json()
            print("Received data:", data)
            
            if not data:
                return make_response(jsonify({
                    'message': 'Không có dữ liệu được gửi lên',
                    'error': 'NO_DATA'
                }), HTTPStatus.BAD_REQUEST)
                
            required_fields = ['name', 'role', 'avatar', 'team', 'department', 'skills', 'links']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return make_response(jsonify({
                    'message': f'Thiếu các trường bắt buộc: {", ".join(missing_fields)}',
                    'error': 'MISSING_FIELDS'
                }), HTTPStatus.BAD_REQUEST)

            new_member = Member.create(data)
            return make_response(jsonify({
                'message': 'Tạo thành viên mới thành công',
                'data': new_member.__dict__
            }), HTTPStatus.CREATED)
            
        except Exception as e:
            print("Error:", str(e))
            return make_response(jsonify({
                'message': 'Lỗi khi tạo thành viên mới',
                'error': str(e)
            }), HTTPStatus.INTERNAL_SERVER_ERROR)

@api.route('/', '/<string:id>')
class MemberResource(Resource):
    @api.doc('get_member')
    def get(self, id):
        """Lấy thông tin một thành viên theo ID"""
        try:
            member = Member.get_by_id(id)
            if member:
                return {
                    'message': 'Lấy thông tin thành viên thành công',
                    'data': member.__dict__
                }, HTTPStatus.OK
            return {
                'message': 'Không tìm thấy thành viên',
                'error': 'NOT_FOUND'
            }, HTTPStatus.NOT_FOUND
        except Exception as e:
            return {
                'message': 'Lỗi khi lấy thông tin thành viên',
                'error': str(e)
            }, HTTPStatus.INTERNAL_SERVER_ERROR

    @api.doc('update_member')
    @api.expect(member_model)
    @jwt_required()
    def put(self, id):
        """Cập nhật thông tin thành viên"""
        try:
            print(f"Attempting to update member with ID: {id}")
            member_id = int(id)
            
            # Kiểm tra member có tồn tại không
            existing_member = Member.get_by_id(member_id)
            if not existing_member:
                print(f"Member with ID {member_id} not found")
                return make_response(jsonify({
                    'message': 'Không tìm thấy thành viên',
                    'error': 'NOT_FOUND'
                }), HTTPStatus.NOT_FOUND)

            # Lấy và kiểm tra dữ liệu gửi lên
            data = request.get_json()
            print(f"Received update data:", data)
            
            if not data:
                print("No data received in update request")
                return make_response(jsonify({
                    'message': 'Không có dữ liệu được gửi lên',
                    'error': 'NO_DATA'
                }), HTTPStatus.BAD_REQUEST)

            # Kiểm tra các trường bắt buộc
            required_fields = ['name', 'role', 'avatar', 'team', 'department', 'skills', 'links']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"Missing required fields: {missing_fields}")
                return make_response(jsonify({
                    'message': f'Thiếu các trường bắt buộc: {", ".join(missing_fields)}',
                    'error': 'MISSING_FIELDS'
                }), HTTPStatus.BAD_REQUEST)

            # Thực hiện cập nhật
            updated_member = Member.update(member_id, data)
            if updated_member:
                print(f"Successfully updated member with ID {member_id}")
                return make_response(jsonify({
                    'message': 'Cập nhật thành viên thành công',
                    'data': updated_member.__dict__
                }), HTTPStatus.OK)
            
            print(f"Failed to update member with ID {member_id}")
            return make_response(jsonify({
                'message': 'Không thể cập nhật thành viên',
                'error': 'UPDATE_FAILED'
            }), HTTPStatus.INTERNAL_SERVER_ERROR)

        except ValueError as ve:
            print(f"Invalid ID format: {id}")
            return make_response(jsonify({
                'message': 'ID không hợp lệ',
                'error': 'INVALID_ID',
                'details': str(ve)
            }), HTTPStatus.BAD_REQUEST)
            
        except Exception as e:
            print(f"Error updating member: {str(e)}")
            return make_response(jsonify({
                'message': 'Lỗi khi cập nhật thành viên',
                'error': 'INTERNAL_ERROR',
                'details': str(e)
            }), HTTPStatus.INTERNAL_SERVER_ERROR)

    @api.doc('delete_member')
    @jwt_required()
    def delete(self, id):
        """Xóa thành viên"""
        try:
            print(f"Attempting to delete member with ID: {id}")
            member_id = int(id)
            
            member = Member.get_by_id(member_id)
            if not member:
                print(f"Member with ID {member_id} not found")
                return make_response(jsonify({
                    'message': 'Không tìm thấy thành viên',
                    'error': 'NOT_FOUND'
                }), HTTPStatus.NOT_FOUND)
            
            if Member.delete(member_id):
                print(f"Successfully deleted member with ID {member_id}")
                return make_response(jsonify({
                    'message': 'Xóa thành viên thành công'
                }), HTTPStatus.OK)
            
            print(f"Failed to delete member with ID {member_id}")
            return make_response(jsonify({
                'message': 'Không thể xóa thành viên',
                'error': 'DELETE_FAILED'
            }), HTTPStatus.INTERNAL_SERVER_ERROR)
            
        except ValueError as ve:
            print(f"Invalid ID format: {id}")
            return make_response(jsonify({
                'message': 'ID không hợp lệ',
                'error': 'INVALID_ID',
                'details': str(ve)
            }), HTTPStatus.BAD_REQUEST)
            
        except Exception as e:
            print(f"Error deleting member: {str(e)}")
            return make_response(jsonify({
                'message': 'Lỗi khi xóa thành viên',
                'error': 'INTERNAL_ERROR',
                'details': str(e)
            }), HTTPStatus.INTERNAL_SERVER_ERROR)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@api.route('/upload-avatar')
class MemberAvatarUpload(Resource):
    @api.doc('upload_member_avatar')
    @jwt_required()
    def post(self):
        """Upload avatar cho thành viên"""
        try:
            if 'avatar' not in request.files:
                return {
                    'message': 'Không tìm thấy file',
                    'error': 'NO_FILE'
                }, HTTPStatus.BAD_REQUEST

            file = request.files['avatar']
            if not file:
                return {
                    'message': 'Không có file nào được chọn',
                    'error': 'NO_FILE_SELECTED'
                }, HTTPStatus.BAD_REQUEST

            # Kiểm tra phần mở rộng
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            if not '.' in file.filename or \
               file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                return {
                    'message': 'Định dạng file không được hỗ trợ',
                    'error': 'INVALID_FILE_TYPE'
                }, HTTPStatus.BAD_REQUEST

            # Tạo tên file an toàn với timestamp
            member_name = request.form.get('name', 'member')
            timestamp = int(time.time())
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            filename = secure_filename(f"{member_name}_{timestamp}.{file_extension}")
            
            # Lưu file
            # Thay đổi từ UPLOAD_FOLDER thành UPLOAD_FOLDER_MEMBERS
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER_MEMBERS'], filename)
            file.save(file_path)

            # Trả về URL của ảnh
            image_url = url_for('serve_member_image', filename=filename, _external=True)
            
            return {
                'message': 'Upload avatar thành công',
                'data': {
                    'url': image_url
                }
            }, HTTPStatus.OK

        except Exception as e:
            print("Error uploading member avatar:", str(e))
            print(traceback.format_exc())
            return {
                'message': 'Lỗi khi upload avatar',
                'error': str(e)
            }, HTTPStatus.INTERNAL_SERVER_ERROR 