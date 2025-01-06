from flask import request, jsonify, make_response, current_app, url_for
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ..models.event import Event
from http import HTTPStatus
import traceback
import os
from werkzeug.utils import secure_filename
import time

api = Namespace('events', description='Quản lý sự kiện')

event_model = api.model('Event', {
    'title': fields.String(required=True),
    'description': fields.String(required=True),
    'date': fields.String(required=True),
    'time': fields.String(required=True),
    'location': fields.String(required=True),
    'status': fields.String(required=True),
    'image': fields.String(required=True),
    'maxParticipants': fields.Integer(required=True),
    'currentParticipants': fields.Integer(required=False),
    'organizer': fields.String(required=False)
})

@api.route('/')
class EventList(Resource):
    @api.doc('list_events')
    def get(self):
        """Lấy danh sách tất cả sự kiện"""
        try:
            Event.update_status()  # Cập nhật trạng thái trước khi trả về
            events = Event.get_all()
            return {
                'message': 'Lấy danh sách sự kiện thành công',
                'data': [event.__dict__ for event in events]
            }, HTTPStatus.OK
        except Exception as e:
            print(f"Error getting events: {str(e)}")
            print(traceback.format_exc())
            return {
                'message': 'Lỗi khi lấy danh sách sự kiện',
                'error': str(e)
            }, HTTPStatus.INTERNAL_SERVER_ERROR

    @api.doc('create_event')
    @api.expect(event_model)
    @jwt_required()
    def post(self):
        """Tạo sự kiện mới"""
        try:
            data = request.get_json()
            new_event = Event.create(data)
            return {
                'message': 'Tạo sự kiện mới thành công',
                'data': new_event.__dict__
            }, HTTPStatus.CREATED
        except ValueError as ve:
            return {
                'message': str(ve),
                'error': 'VALIDATION_ERROR'
            }, HTTPStatus.BAD_REQUEST
        except Exception as e:
            print(f"Error creating event: {str(e)}")
            print(traceback.format_exc())
            return {
                'message': 'Lỗi khi tạo sự kiện mới',
                'error': str(e)
            }, HTTPStatus.INTERNAL_SERVER_ERROR

@api.route('/<int:id>')
class EventResource(Resource):
    @api.doc('get_event')
    def get(self, id):
        """Lấy thông tin một sự kiện"""
        try:
            event = Event.get_by_id(id)
            if event:
                return {
                    'message': 'Lấy thông tin sự kiện thành công',
                    'data': event.__dict__
                }, HTTPStatus.OK
            return {
                'message': 'Không tìm thấy sự kiện',
                'error': 'NOT_FOUND'
            }, HTTPStatus.NOT_FOUND
        except Exception as e:
            return {
                'message': 'Lỗi khi lấy thông tin sự kiện',
                'error': str(e)
            }, HTTPStatus.INTERNAL_SERVER_ERROR

    @api.doc('update_event')
    @api.expect(event_model)
    @jwt_required()
    def put(self, id):
        """Cập nhật thông tin sự kiện"""
        try:
            data = request.get_json()
            updated_event = Event.update(id, data)
            if updated_event:
                return {
                    'message': 'Cập nhật sự kiện thành công',
                    'data': updated_event.__dict__
                }, HTTPStatus.OK
            return {
                'message': 'Không tìm thấy sự kiện',
                'error': 'NOT_FOUND'
            }, HTTPStatus.NOT_FOUND
        except Exception as e:
            return {
                'message': 'Lỗi khi cập nhật sự kiện',
                'error': str(e)
            }, HTTPStatus.INTERNAL_SERVER_ERROR

    @api.doc('delete_event')
    @jwt_required()
    def delete(self, id):
        """Xóa sự kiện"""
        try:
            if Event.delete(id):
                return {
                    'message': 'Xóa sự kiện thành công'
                }, HTTPStatus.OK
            return {
                'message': 'Không tìm thấy sự kiện',
                'error': 'NOT_FOUND'
            }, HTTPStatus.NOT_FOUND
        except Exception as e:
            return {
                'message': 'Lỗi khi xóa sự kiện',
                'error': str(e)
            }, HTTPStatus.INTERNAL_SERVER_ERROR

@api.route('/upload-image')
class EventImageUpload(Resource):
    @api.doc('upload_event_image')
    @jwt_required()
    def post(self):
        """Upload ảnh cho sự kiện"""
        try:
            if 'image' not in request.files:
                return {
                    'message': 'Không tìm thấy file',
                    'error': 'NO_FILE'
                }, HTTPStatus.BAD_REQUEST

            file = request.files['image']
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
            event_title = request.form.get('title', 'event')
            timestamp = int(time.time())
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            filename = secure_filename(f"{event_title}_{timestamp}.{file_extension}")
            
            # Lưu file
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER_EVENTS'], filename)
            file.save(file_path)

            # Trả về URL của ảnh
            image_url = url_for('serve_event_image', filename=filename, _external=True)
            
            return {
                'message': 'Upload ảnh thành công',
                'data': {
                    'url': image_url
                }
            }, HTTPStatus.OK

        except Exception as e:
            print("Error uploading event image:", str(e))
            print(traceback.format_exc())
            return {
                'message': 'Lỗi khi upload ảnh',
                'error': str(e)
            }, HTTPStatus.INTERNAL_SERVER_ERROR 

@api.route('/<int:id>/register')
class EventRegistration(Resource):
    @api.doc('register_event')
    def post(self, id):
        """Xác nhận tham gia sự kiện"""
        try:
            # Lấy IP của người dùng
            ip_address = request.remote_addr
            if request.headers.getlist("X-Forwarded-For"):
                ip_address = request.headers.getlist("X-Forwarded-For")[0]

            event, status = Event.increment_participants(id, ip_address)
            
            if status == "SUCCESS":
                return {
                    'message': 'Đăng ký tham gia thành công',
                    'data': event.__dict__
                }, HTTPStatus.OK
            elif status == "IP_ALREADY_REGISTERED":
                return {
                    'message': 'Bạn đã đăng ký tham gia sự kiện này rồi',
                    'error': 'IP_ALREADY_REGISTERED'
                }, HTTPStatus.BAD_REQUEST
            elif status == "FULL_CAPACITY":
                return {
                    'message': 'Sự kiện đã đủ số lượng người tham gia',
                    'error': 'FULL_CAPACITY'
                }, HTTPStatus.BAD_REQUEST
            else:
                return {
                    'message': 'Không tìm thấy sự kiện',
                    'error': 'NOT_FOUND'
                }, HTTPStatus.NOT_FOUND

        except Exception as e:
            print("Error registering for event:", str(e))
            print(traceback.format_exc())
            return {
                'message': 'Lỗi khi đăng ký tham gia',
                'error': str(e)
            }, HTTPStatus.INTERNAL_SERVER_ERROR 