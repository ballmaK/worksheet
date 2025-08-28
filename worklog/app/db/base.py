# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa
from app.models.team import Team  # noqa
from app.models.team_member import TeamMember  # noqa
from app.models.project import Project  # noqa
from app.models.work_log import WorkLog, Comment  # noqa
from app.models.reminder import Reminder  # noqa
from app.models.work_log_template import WorkLogTemplate  # noqa
from app.models.task import Task, TaskDependency, TaskComment, TaskAttachment  # noqa
from app.models.task_log import TaskLog, TaskStatusChange  # noqa
from app.models.message import Message, MessageTemplate  # noqa

# 导入所有模型，以便 Alembic 可以检测到它们 

# 所有模型导入后，最后建立User与WorkLogTemplate的关系，避免循环依赖
from sqlalchemy.orm import relationship
User.templates = relationship("WorkLogTemplate", back_populates="user", cascade="all, delete-orphan") 