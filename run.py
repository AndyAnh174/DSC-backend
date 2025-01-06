from app import create_app
from app.models.user import User
from config import Config

app = create_app()

@app.cli.command("init-db")
def init_db():
    """Khởi tạo database và tạo tài khoản admin mặc định"""
    # Tạo tài khoản admin mặc định nếu chưa tồn tại
    admin = User.get_by_username(Config.ADMIN_USERNAME)
    if not admin:
        admin = User.create(
            username=Config.ADMIN_USERNAME,
            password=Config.ADMIN_PASSWORD,
            role='admin'
        )
        print(f'Đã tạo tài khoản admin mặc định (username: {Config.ADMIN_USERNAME})')
    else:
        print('Tài khoản admin đã tồn tại')
    
    print('Khởi tạo database hoàn tất') 