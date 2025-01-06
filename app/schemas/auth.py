from flask_restx import fields, Namespace

api = Namespace('auth', description='Authentication operations')

login_request = api.model('LoginRequest', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})

user_model = api.model('User', {
    'id': fields.Integer(description='User ID'),
    'username': fields.String(description='Username'),
    'role': fields.String(description='User role')
})

login_response = api.model('LoginResponse', {
    'access_token': fields.String(description='JWT access token'),
    'user': fields.Nested(user_model)
})

error_response = api.model('ErrorResponse', {
    'message': fields.String(description='Error message'),
    'errors': fields.Raw(description='Validation errors')
}) 