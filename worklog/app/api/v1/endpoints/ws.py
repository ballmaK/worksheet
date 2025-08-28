from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException
from app.core.ws_manager import ws_manager
from app.core.security import get_current_user_from_token
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from typing import Optional
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

async def get_user_id_from_token(token: str = Query(...), db: Session = Depends(get_db)) -> int:
    try:
        user = get_current_user_from_token(token, db)
        if not user:
            raise HTTPException(status_code=401, detail="无效token")
        return user.id
    except Exception as e:
        logger.error(f"验证token失败: {e}")
        raise HTTPException(status_code=401, detail="token验证失败")

@router.websocket("/ws/messages/")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int = Depends(get_user_id_from_token)
):
    await ws_manager.connect(user_id, websocket)
    logger.info(f"用户 {user_id} 建立WebSocket连接")
    
    try:
        while True:
            # 等待客户端消息（心跳或命令）
            data = await websocket.receive_text()
            try:
                # 尝试解析JSON消息
                message = json.loads(data)
                message_type = message.get("type", "heartbeat")
                
                if message_type == "heartbeat":
                    # 心跳响应
                    await websocket.send_text(json.dumps({
                        "type": "heartbeat",
                        "status": "ok"
                    }))
                elif message_type == "ping":
                    # Ping响应
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    }))
                else:
                    # 其他消息类型
                    logger.info(f"收到用户 {user_id} 的消息: {message_type}")
                    await websocket.send_text(json.dumps({
                        "type": "ack",
                        "message": "消息已收到"
                    }))
                    
            except json.JSONDecodeError:
                # 如果不是JSON，当作心跳处理
                await websocket.send_text(json.dumps({
                    "type": "heartbeat",
                    "status": "ok"
                }))
                
    except WebSocketDisconnect:
        await ws_manager.disconnect(user_id, websocket)
        logger.info(f"用户 {user_id} WebSocket连接断开")
    except Exception as e:
        logger.error(f"WebSocket连接异常: {e}")
        await ws_manager.disconnect(user_id, websocket) 