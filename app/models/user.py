import json
import os
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional
from config import Config

class User:
    def __init__(self, id: int, username: str, password_hash: str, role: str = 'user', **kwargs):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role

    @staticmethod
    def get_db_path() -> str:
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                           'data', 'db.json')

    @classmethod
    def load_all(cls) -> list['User']:
        try:
            with open(cls.get_db_path(), 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [cls(**user) for user in data.get('users', [])]
        except FileNotFoundError:
            return []

    @classmethod
    def save_all(cls, users: list['User']) -> None:
        with open(cls.get_db_path(), 'w', encoding='utf-8') as f:
            json.dump({
                'users': [
                    {
                        'id': user.id,
                        'username': user.username,
                        'password_hash': user.password_hash,
                        'role': user.role
                    }
                    for user in users
                ]
            }, f, ensure_ascii=False, indent=2)

    @classmethod
    def get_by_username(cls, username: str) -> Optional['User']:
        users = cls.load_all()
        return next((u for u in users if u.username == username), None)

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    def generate_token(self) -> str:
        expires = datetime.utcnow() + timedelta(hours=24)
        return jwt.encode(
            {
                'sub': str(self.id),
                'user_id': self.id,
                'username': self.username,
                'role': self.role,
                'exp': expires,
                'iat': datetime.utcnow()
            },
            Config.JWT_SECRET_KEY,
            algorithm='HS256'
        ) 