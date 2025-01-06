from flask import Flask, send_from_directory, request
from flask_restx import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from .routes.auth import api as auth_ns, blacklisted_tokens
from .routes.member import api as member_ns
from .routes.event import api as event_ns
from .routes.project import api as project_ns
from .routes.contact import api as contact_ns
from .routes.banner import api as banner_ns
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Thêm config cho upload
    app.config['UPLOAD_FOLDER_MEMBERS'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images', 'members')
    app.config['UPLOAD_FOLDER_EVENTS'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images', 'events')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit
    
    # Đảm bảo thư mục upload tồn tại
    os.makedirs(app.config['UPLOAD_FOLDER_MEMBERS'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER_EVENTS'], exist_ok=True)

    # Route để serve static files
    @app.route('/static/images/members/<path:filename>')
    def serve_member_image(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER_MEMBERS'], filename)

    @app.route('/static/images/events/<path:filename>')
    def serve_event_image(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER_EVENTS'], filename)

    # Thêm config cho upload banner
    app.config['UPLOAD_FOLDER_BANNERS'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images', 'banners')
    os.makedirs(app.config['UPLOAD_FOLDER_BANNERS'], exist_ok=True)
    
    # Thêm route để serve banner images
    @app.route('/static/images/banners/<path:filename>')
    def serve_banner_image(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER_BANNERS'], filename)

    # Thêm cấu hình này để tắt tự động thêm dấu / vào cuối URL
    app.url_map.strict_slashes = False
    
    # Cấu hình JWT
    jwt = JWTManager(app)
    
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return jti in blacklisted_tokens
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {
            'message': 'Token đã hết hạn',
            'error': 'TOKEN_EXPIRED'
        }, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {
            'message': 'Token không hợp lệ',
            'error': 'INVALID_TOKEN'
        }, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {
            'message': 'Thiếu token xác thực',
            'error': 'MISSING_TOKEN'
        }, 401
    
    # Cấu hình CORS mới
    CORS(app, resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",
                "https://hcmute-dsc.vercel.app",
                "https://partially-surgeon-long-fridge.trycloudflare.com"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Origin"],
            "expose_headers": ["Content-Type"],
            "supports_credentials": True
        }
    })
    
    # Thêm handler cho OPTIONS request cho tất cả các route
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin in [
            "http://localhost:5173",
            "https://hcmute-dsc.vercel.app",
            "https://partially-surgeon-long-fridge.trycloudflare.com"
        ]:
            response.headers.add('Access-Control-Allow-Origin', origin)
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    api = Api(
        app,
        version='1.0',
        title='DSC UTE API',
        description='API cho website DSC UTE',
        doc='/docs',
        authorizations={
            'Bearer': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
            }
        },
        security='Bearer'
    )
    
    api.add_namespace(auth_ns)
    api.add_namespace(member_ns, path='/members')
    api.add_namespace(event_ns, path='/events')
    api.add_namespace(project_ns, path='/projects')
    api.add_namespace(contact_ns, path='/contacts')
    api.add_namespace(banner_ns, path='/banners')
    
    return app 