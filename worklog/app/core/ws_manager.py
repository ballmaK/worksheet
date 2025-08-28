from typing import Dict, List, Any
from fastapi import WebSocket
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # user_id -> List[WebSocket]
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.lock = asyncio.Lock()

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        async with self.lock:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)
        logger.info(f"用户 {user_id} 已连接WebSocket")

    async def disconnect(self, user_id: int, websocket: WebSocket):
        async with self.lock:
            if user_id in self.active_connections:
                if websocket in self.active_connections[user_id]:
                    self.active_connections[user_id].remove(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
        logger.info(f"用户 {user_id} 已断开WebSocket连接")

    async def send_personal_message(self, user_id: int, message: str):
        """发送文本消息给指定用户"""
        async with self.lock:
            conns = self.active_connections.get(user_id, [])
            for ws in conns:
                try:
                    await ws.send_text(message)
                except Exception as e:
                    logger.error(f"发送消息给用户 {user_id} 失败: {e}")
                    # 移除断开的连接
                    if ws in conns:
                        conns.remove(ws)

    async def send_json_message(self, user_id: int, data: Any):
        """发送JSON消息给指定用户"""
        try:
            message = json.dumps(data, ensure_ascii=False)
            await self.send_personal_message(user_id, message)
        except Exception as e:
            logger.error(f"发送JSON消息给用户 {user_id} 失败: {e}")

    async def send_team_message(self, team_member_ids: List[int], data: Any):
        """发送消息给团队成员"""
        message = json.dumps(data, ensure_ascii=False)
        async with self.lock:
            for user_id in team_member_ids:
                conns = self.active_connections.get(user_id, [])
                for ws in conns:
                    try:
                        await ws.send_text(message)
                    except Exception as e:
                        logger.error(f"发送团队消息给用户 {user_id} 失败: {e}")
                        # 移除断开的连接
                        if ws in conns:
                            conns.remove(ws)

    async def broadcast(self, message: str):
        """广播消息给所有连接的用户"""
        async with self.lock:
            for user_id, conns in self.active_connections.items():
                for ws in conns:
                    try:
                        await ws.send_text(message)
                    except Exception as e:
                        logger.error(f"广播消息给用户 {user_id} 失败: {e}")
                        # 移除断开的连接
                        if ws in conns:
                            conns.remove(ws)

    def get_connected_users(self) -> List[int]:
        """获取当前连接的用户ID列表"""
        return list(self.active_connections.keys())

    def is_user_connected(self, user_id: int) -> bool:
        """检查用户是否在线"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0

ws_manager = ConnectionManager() 