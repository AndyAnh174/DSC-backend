import os
from flask import request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
import logging
import time
from flask_cors import CORS

# Cấu hình logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={
    r"/upload": {"origins": ["http://localhost:5173","https://harbour-tyler-same-microwave.trycloudflare.com"]}, # Thay port frontend nếu khác
    r"/static/*": {"origins": "*"}
})

# Cấu hình static folder
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images')

# Route để serve static files
@app.route('/static/images/<path:folder>/<path:filename>')
def serve_image(folder, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], folder), filename)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
@jwt_required() #check cho kĩ vò trước khi sử dug caiài jwt tại vì nếu up load ảnh thì ko cần thiết
def upload_file():
    try:
        logger.info('Starting file upload')
        logger.debug(f'Request files: {request.files}')
        logger.debug(f'Request form: {request.form}')
        logger.debug(f'Request headers: {dict(request.headers)}')
        
        if 'file' not in request.files:
            logger.error('No file part in request')
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        folder = request.form.get('folder', 'others')
        
        logger.info(f'Processing upload for file: {file.filename} to folder: {folder}')
        logger.debug(f'File details: size={len(file.read())} bytes, type={file.content_type}')
        file.seek(0)  # Reset file pointer after reading
        
        if file.filename == '':
            logger.error('No selected file')
            return jsonify({'error': 'No selected file'}), 400
            
        if file and allowed_file(file.filename):
            filename = f"{os.path.splitext(secure_filename(file.filename))[0]}_{int(time.time())}{os.path.splitext(file.filename)[1]}"
            logger.debug(f'Secured filename: {filename}')
            
            folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
            logger.debug(f'Full folder path: {os.path.abspath(folder_path)}')
            
            # Kiểm tra quyền ghi
            if not os.access(os.path.dirname(folder_path), os.W_OK):
                logger.error(f'No write permission for folder: {folder_path}')
                return jsonify({'error': 'No write permission for upload folder'}), 500
            
            if not os.path.exists(folder_path):
                logger.info(f'Creating folder: {folder_path}')
                try:
                    os.makedirs(folder_path, exist_ok=True)
                except Exception as mkdir_error:
                    logger.error(f'Error creating folder: {str(mkdir_error)}')
                    return jsonify({'error': f'Could not create upload folder: {str(mkdir_error)}'}), 500
            
            file_path = os.path.join(folder_path, filename)
            logger.info(f'Saving file to: {file_path}')
            
            try:
                file.save(file_path)
                logger.info('File saved successfully')
                file_size = os.path.getsize(file_path)
                logger.debug(f'Saved file size: {file_size} bytes')
            except Exception as save_error:
                logger.error(f'Error saving file: {str(save_error)}')
                logger.exception(save_error)
                return jsonify({'error': f'Error saving file: {str(save_error)}'}), 500
            
            url = f'/static/images/{folder}/{filename}'
            logger.info(f'File uploaded successfully. URL: {url}')
            return jsonify({'url': url}), 200
            
        logger.error(f'Invalid file type: {file.filename}')
        return jsonify({'error': 'File type not allowed'}), 400
        
    except Exception as e:
        logger.error(f'Unexpected error in upload_file: {str(e)}')
        logger.exception(e)
        return jsonify({
            'error': str(e),
            'traceback': str(e.__traceback__),
            'type': str(type(e))
        }), 500 

if __name__ == '__main__':
    # Tạo thư mục static/images nếu chưa tồn tại
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True) 