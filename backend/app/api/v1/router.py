from fastapi import APIRouter

from backend.app.api.v1.auth import router_auth
from backend.app.api.v1.monitor import router_monitor, router_monitor_nested
from backend.app.api.v1.protected import router_protected
from backend.app.api.v1.workspace import router_workspace

api_router = APIRouter()
api_router.include_router(router_auth)
api_router.include_router(router_protected)
api_router.include_router(router_workspace)
api_router.include_router(router_monitor)
api_router.include_router(router_monitor_nested)
# api_router.include_router(router_ping_history)
