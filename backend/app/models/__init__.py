# import all models here to ensure they are registered with the Base for Alembic migrations

from backend.app.db.database import Base

from .monitor import Monitor
from .ping_history import PingHistory
from .user import User
from .workspace import Workspace, WorkspaceUser

# optional: we can now import in other modules to use the models, e.g. from app.models import User
