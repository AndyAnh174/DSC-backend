import json
import os
from typing import List, Optional, Dict

class Project:
    def __init__(
        self,
        id: int,
        title: str,
        description: str,
        category: str,
        image: str,
        progress: int,
        teamSize: int,
        technologies: List[str],
        links: Dict[str, str],
        details: str = "",  # Thêm trường chi tiết dự án
        teamMembers: List[Dict] = None  # Thêm thông tin thành viên
    ):
        self.id = id
        self.title = title
        self.description = description
        self.category = category
        self.image = image
        self.progress = progress
        self.teamSize = teamSize
        self.technologies = technologies
        self.links = links
        self.details = details
        self.teamMembers = teamMembers or []

    @staticmethod
    def get_data_file_path() -> str:
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'projects.json')

    @classmethod
    def get_all(cls) -> List['Project']:
        try:
            with open(cls.get_data_file_path(), 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [cls(**project) for project in data.get('projects', [])]
        except FileNotFoundError:
            return []

    @classmethod
    def save_all(cls, projects: List['Project']) -> None:
        data = {
            'projects': [project.__dict__ for project in projects]
        }
        with open(cls.get_data_file_path(), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def create(cls, project_data: dict) -> 'Project':
        projects = cls.get_all()
        new_id = max([p.id for p in projects], default=0) + 1
        project_data['id'] = new_id
        new_project = cls(**project_data)
        projects.append(new_project)
        cls.save_all(projects)
        return new_project

    @classmethod
    def get_by_id(cls, id: int) -> Optional['Project']:
        projects = cls.get_all()
        return next((p for p in projects if p.id == id), None)

    @classmethod
    def update(cls, id: int, project_data: dict) -> Optional['Project']:
        projects = cls.get_all()
        for i, project in enumerate(projects):
            if project.id == id:
                project_data['id'] = id
                updated_project = cls(**project_data)
                projects[i] = updated_project
                cls.save_all(projects)
                return updated_project
        return None

    @classmethod
    def delete(cls, id: int) -> bool:
        projects = cls.get_all()
        initial_length = len(projects)
        projects = [p for p in projects if p.id != id]
        if len(projects) < initial_length:
            cls.save_all(projects)
            return True
        return False 