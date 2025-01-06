import json
import os
from typing import List, Optional, Dict
from datetime import datetime

class Event:
    def __init__(
        self,
        id: int,
        title: str,
        description: str,
        date: str,
        time: str,
        location: str,
        status: str,
        image: str,
        maxParticipants: int,
        currentParticipants: int = 0,
        organizer: str = "DSC UTE",
        googleFormUrl: str = "",
        registered_ips: List[str] = None
    ):
        self.id = id
        self.title = title
        self.description = description
        self.date = date
        self.time = time
        self.location = location
        self.status = status
        self.image = image
        self.maxParticipants = maxParticipants
        self.currentParticipants = currentParticipants
        self.organizer = organizer
        self.googleFormUrl = googleFormUrl
        self.registered_ips = registered_ips or []

    @staticmethod
    def get_data_file_path() -> str:
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'events.json')

    @classmethod
    def get_all(cls) -> List['Event']:
        try:
            with open(cls.get_data_file_path(), 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [cls(**event) for event in data.get('events', [])]
        except FileNotFoundError:
            return []

    @classmethod
    def save_all(cls, events: List['Event']) -> None:
        data = {
            'events': [event.__dict__ for event in events]
        }
        with open(cls.get_data_file_path(), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def create(cls, event_data: dict) -> 'Event':
        events = cls.get_all()
        new_id = max([e.id for e in events], default=0) + 1
        event_data['id'] = new_id
        
        # Validate date format
        try:
            datetime.strptime(event_data['date'], '%Y-%m-%d')
        except ValueError:
            raise ValueError('Invalid date format. Use YYYY-MM-DD')

        new_event = cls(**event_data)
        events.append(new_event)
        cls.save_all(events)
        return new_event

    @classmethod
    def update(cls, id: int, event_data: dict) -> Optional['Event']:
        events = cls.get_all()
        for i, event in enumerate(events):
            if event.id == id:
                event_data['id'] = id
                updated_event = cls(**event_data)
                events[i] = updated_event
                cls.save_all(events)
                return updated_event
        return None

    @classmethod
    def delete(cls, id: int) -> bool:
        events = cls.get_all()
        initial_length = len(events)
        events = [e for e in events if e.id != id]
        if len(events) < initial_length:
            cls.save_all(events)
            return True
        return False

    @classmethod
    def get_by_id(cls, id: int) -> Optional['Event']:
        events = cls.get_all()
        return next((e for e in events if e.id == id), None)

    @classmethod
    def update_status(cls) -> None:
        """Cập nhật trạng thái sự kiện dựa trên ngày"""
        events = cls.get_all()
        today = datetime.now().date()
        
        for event in events:
            event_date = datetime.strptime(event.date, '%Y-%m-%d').date()
            if event_date < today:
                event.status = 'past'
            elif event_date == today:
                event.status = 'ongoing'
            else:
                event.status = 'upcoming'
        
        cls.save_all(events) 

    @classmethod
    def increment_participants(cls, id: int, ip_address: str) -> tuple[Optional['Event'], str]:
        """Tăng số người tham gia và kiểm tra IP"""
        events = cls.get_all()
        for i, event in enumerate(events):
            if event.id == id:
                # Kiểm tra IP đã đăng ký chưa
                if ip_address in event.registered_ips:
                    return None, "IP_ALREADY_REGISTERED"
                
                # Kiểm tra số lượng
                if event.currentParticipants >= event.maxParticipants:
                    return None, "FULL_CAPACITY"
                
                # Tăng số người tham gia và thêm IP
                event.currentParticipants += 1
                event.registered_ips.append(ip_address)
                cls.save_all(events)
                return event, "SUCCESS"
                
        return None, "NOT_FOUND" 