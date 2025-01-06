import json
import os
from typing import List, Optional, Dict

class Member:
    DEFAULT_AVATAR = '/static/images/members/default-avatar.png'
    
    def __init__(
        self,
        id: int,
        name: str,
        role: str,
        team: str,
        department: str,
        avatar: str = None,
        year: Optional[str] = None,
        skills: List[str] = None,
        links: Dict[str, str] = None
    ):
        self.id = id
        self.name = name
        self.role = role
        self.team = team
        self.department = department
        self.avatar = avatar if avatar else self.DEFAULT_AVATAR
        self.year = year
        self.skills = skills or []
        self.links = links or {
            'facebook': 'https://facebook.com',
            'github': 'https://github.com',
            'email': ''
        }

    @staticmethod
    def get_data_file_path() -> str:
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'members.json')

    @classmethod
    def get_all(cls) -> List['Member']:
        try:
            with open(cls.get_data_file_path(), 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [cls(**member) for member in data.get('members', [])]
        except FileNotFoundError:
            return []

    @classmethod
    def save_all(cls, members: List['Member']) -> None:
        data = {
            'members': [member.__dict__ for member in members]
        }
        with open(cls.get_data_file_path(), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def create(cls, member_data: dict) -> 'Member':
        members = cls.get_all()
        # Tạo ID mới
        new_id = max([m.id for m in members], default=0) + 1
        member_data['id'] = new_id
        
        new_member = cls(**member_data)
        members.append(new_member)
        cls.save_all(members)
        return new_member

    @classmethod
    def update(cls, id: int, member_data: dict) -> Optional['Member']:
        try:
            print(f"Updating member with ID: {id}")
            print(f"Update data: {member_data}")
            
            members = cls.get_all()
            for i, member in enumerate(members):
                if member.id == id:
                    # Giữ nguyên ID
                    member_data['id'] = id
                    
                    # Tạo member mới với dữ liệu cập nhật
                    try:
                        updated_member = cls(**member_data)
                        print(f"Created updated member object: {updated_member.__dict__}")
                    except Exception as e:
                        print(f"Error creating updated member object: {str(e)}")
                        raise
                    
                    # Cập nhật trong danh sách
                    members[i] = updated_member
                    
                    try:
                        # Lưu vào file
                        cls.save_all(members)
                        print(f"Successfully saved updated member with ID: {id}")
                    except Exception as e:
                        print(f"Error saving member data: {str(e)}")
                        raise
                    
                    return updated_member
                    
            print(f"No member found with ID: {id}")
            return None
            
        except Exception as e:
            print(f"Error in update operation: {str(e)}")
            raise

    @classmethod
    def delete(cls, id: int) -> bool:
        try:
            print(f"Deleting member with ID: {id}")  # Thêm log
            members = cls.get_all()
            initial_length = len(members)
            members = [m for m in members if m.id != id]
            
            if len(members) < initial_length:
                print(f"Member found and filtered out, saving changes...")  # Thêm log
                cls.save_all(members)
                print(f"Successfully deleted member with ID: {id}")  # Thêm log
                return True
                
            print(f"No member found with ID: {id}")  # Thêm log
            return False
            
        except Exception as e:
            print(f"Error in delete operation: {str(e)}")  # Thêm log
            raise e

    @classmethod
    def get_by_id(cls, id: int) -> Optional['Member']:
        members = cls.get_all()
        return next((m for m in members if m.id == id), None) 