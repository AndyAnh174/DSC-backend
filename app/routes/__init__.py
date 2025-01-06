from .auth import api as auth_ns
from .member import api as member_ns
from .event import api as event_ns
from .project import api as project_ns
from .contact import api as contact_ns
from .banner import api as banner_ns

__all__ = ['auth_ns', 'member_ns', 'event_ns', 'project_ns', 'contact_ns', 'banner_ns'] 