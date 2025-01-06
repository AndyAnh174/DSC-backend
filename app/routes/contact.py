from flask import jsonify, request
from flask_restx import Namespace, Resource
import json
import os
from datetime import datetime
import logging

api = Namespace('contacts', description='Quản lý thông tin liên hệ')

CONTACTS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'contacts.json')

# Đảm bảo thư mục data tồn tại
os.makedirs(os.path.dirname(CONTACTS_FILE), exist_ok=True)

# Đảm bảo file contacts.json tồn tại
if not os.path.exists(CONTACTS_FILE):
    with open(CONTACTS_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

def load_contacts():
    try:
        with open(CONTACTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_contacts(contacts):
    try:
        # Kiểm tra quyền ghi
        if not os.access(os.path.dirname(CONTACTS_FILE), os.W_OK):
            raise PermissionError(f'No write permission for {CONTACTS_FILE}')
            
        with open(CONTACTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(contacts, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f'Error saving contacts: {str(e)}', exc_info=True)
        raise

# Cấu hình logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

@api.route('')
class ContactList(Resource):
    def get(self):
        """Lấy danh sách liên hệ"""
        try:
            contacts = load_contacts()
            # Sắp xếp theo thời gian tạo giảm dần
            contacts.sort(key=lambda x: x['created_at'], reverse=True)
            return contacts
        except Exception as e:
            return [], 200

    def post(self):
        """Thêm liên hệ mới"""
        try:
            logger.debug('Receiving contact form data')
            data = request.get_json()
            if not data:
                logger.error('No JSON data received')
                return {'error': 'Invalid request data'}, 400
                
            logger.debug(f'Received data: {data}')
            
            # Validate dữ liệu trước khi load contacts
            required_fields = ['name', 'email', 'subject', 'message']
            for field in required_fields:
                if not data.get(field):
                    logger.error(f'Missing field: {field}')
                    return {'error': f'Thiếu trường {field}'}, 400

            try:
                contacts = load_contacts()
            except Exception as e:
                logger.error(f'Error loading contacts: {str(e)}')
                contacts = []

            new_contact = {
                'id': len(contacts) + 1,
                'name': data['name'],
                'email': data['email'],
                'subject': data['subject'],
                'message': data['message'],
                'created_at': datetime.now().isoformat()
            }
            
            try:
                contacts.append(new_contact)
                save_contacts(contacts)
                logger.info('Contact saved successfully')
                return new_contact, 201
            except Exception as e:
                logger.error(f'Error saving contact: {str(e)}')
                return {'error': 'Could not save contact'}, 500
                
        except Exception as e:
            logger.error(f'Unexpected error: {str(e)}', exc_info=True)
            return {'error': 'Internal server error'}, 500

@api.route('/<int:id>')
class ContactDetail(Resource):
    def delete(self, id):
        """Xóa một liên hệ"""
        try:
            contacts = load_contacts()
            contacts = [c for c in contacts if c['id'] != id]
            save_contacts(contacts)
            return '', 204
        except Exception as e:
            return {'error': str(e)}, 500 