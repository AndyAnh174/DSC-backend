from flask import jsonify, request
from flask_restx import Namespace, Resource
import json
import os
from datetime import datetime
import logging
from werkzeug.utils import secure_filename
import time

api = Namespace('banners', description='Quản lý banner')

# Cấu hình logger
logger = logging.getLogger(__name__)

BANNERS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'banners.json')
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'images', 'banners')

# Tạo thư mục nếu chưa tồn tại
os.makedirs(os.path.dirname(BANNERS_FILE), exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if not os.path.exists(BANNERS_FILE):
    with open(BANNERS_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_banners():
    try:
        with open(BANNERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_banners(banners):
    with open(BANNERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(banners, f, ensure_ascii=False, indent=2)

@api.route('')
class BannerList(Resource):
    def get(self):
        """Lấy danh sách banner"""
        try:
            banners = load_banners()
            banners.sort(key=lambda x: (x['order'], x['created_at']))
            return {'data': banners}, 200
        except Exception as e:
            logger.error(f'Error getting banners: {str(e)}')
            return {'error': 'Internal server error'}, 500

    def post(self):
        """Thêm banner mới"""
        try:
            if 'image' not in request.files:
                return {'error': 'No image file'}, 400

            file = request.files['image']
            if file.filename == '':
                return {'error': 'No selected file'}, 400

            if file and allowed_file(file.filename):
                filename = f"banner_{int(time.time())}_{secure_filename(file.filename)}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                
                try:
                    file.save(filepath)
                except Exception as e:
                    logger.error(f'Error saving file: {str(e)}')
                    return {'error': 'Could not save file'}, 500

                try:
                    banners = load_banners()
                    new_banner = {
                        'id': len(banners) + 1,
                        'title': request.form.get('title', ''),
                        'description': request.form.get('description', ''),
                        'image': f'/static/images/banners/{filename}',
                        'order': int(request.form.get('order', len(banners) + 1)),
                        'active': request.form.get('active', 'true').lower() == 'true',
                        'created_at': datetime.now().isoformat()
                    }

                    banners.append(new_banner)
                    save_banners(banners)
                    return {'data': new_banner}, 201
                except Exception as e:
                    logger.error(f'Error saving banner data: {str(e)}')
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    return {'error': 'Could not save banner data'}, 500
            
            return {'error': 'File type not allowed'}, 400

        except Exception as e:
            logger.error(f'Error creating banner: {str(e)}')
            return {'error': str(e)}, 500

@api.route('/<int:id>')
class BannerDetail(Resource):
    def put(self, id):
        """Cập nhật banner"""
        try:
            banners = load_banners()
            banner = next((b for b in banners if b['id'] == id), None)
            
            if not banner:
                return {'error': 'Banner not found'}, 404

            if 'image' in request.files:
                file = request.files['image']
                if file.filename != '' and allowed_file(file.filename):
                    # Xóa ảnh cũ nếu tồn tại
                    old_image = banner['image'].split('/')[-1]
                    old_path = os.path.join(UPLOAD_FOLDER, old_image)
                    if os.path.exists(old_path):
                        os.remove(old_path)

                    # Lưu ảnh mới
                    filename = f"banner_{int(time.time())}_{secure_filename(file.filename)}"
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    banner['image'] = f'/static/images/banners/{filename}'

            # Cập nhật các trường khác
            banner['title'] = request.form.get('title', banner['title'])
            banner['description'] = request.form.get('description', banner['description'])
            banner['order'] = int(request.form.get('order', banner['order']))
            banner['active'] = request.form.get('active', str(banner['active'])).lower() == 'true'

            save_banners(banners)
            return {'data': banner}, 200

        except Exception as e:
            logger.error(f'Error updating banner: {str(e)}')
            return {'error': 'Internal server error'}, 500

    def delete(self, id):
        """Xóa banner"""
        try:
            banners = load_banners()
            banner = next((b for b in banners if b['id'] == id), None)
            
            if not banner:
                return {'error': 'Banner not found'}, 404

            # Xóa file ảnh
            image_path = os.path.join(UPLOAD_FOLDER, banner['image'].split('/')[-1])
            if os.path.exists(image_path):
                os.remove(image_path)

            # Xóa banner khỏi danh sách
            banners = [b for b in banners if b['id'] != id]
            save_banners(banners)

            return '', 204

        except Exception as e:
            logger.error(f'Error deleting banner: {str(e)}')
            return {'error': 'Internal server error'}, 500 