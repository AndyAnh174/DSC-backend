from flask_restx import fields

member_schema = {
    'name': fields.String(required=True, description='Tên thành viên'),
    'role': fields.String(required=True, description='Vai trò trong CLB'),
    'avatar': fields.String(required=True, description='Đường dẫn ảnh đại diện'),
    'team': fields.String(required=True, description='Tên team'),
    'department': fields.String(required=True, description='Phòng ban'),
    'year': fields.String(required=True, description='Năm hoạt động'),
    'skills': fields.List(fields.String, required=True, description='Các kỹ năng'),
    'links': fields.Raw(required=True, description='Các liên kết mạng xã hội')
} 