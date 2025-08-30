from fastapi import APIRouter
from app.api.v1.endpoints import users, work_logs, reminders, templates, team, project, tasks, messages, ws, project_management

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(work_logs.router, prefix="/work-logs", tags=["work-logs"])
api_router.include_router(reminders.router, prefix="/reminders", tags=["reminders"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(team.router, prefix="/teams", tags=["teams"])
api_router.include_router(project.router, prefix="/projects", tags=["projects"])
api_router.include_router(project_management.router, prefix="/project-management", tags=["project-management"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(ws.router, tags=["websocket"]) 