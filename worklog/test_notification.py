#!/usr/bin/env python3
"""
通知功能测试脚本
"""

import asyncio
import logging
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.message_service import message_push_service
from app.models.task import Task
from app.models.user import User

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_task_notification():
    """测试任务通知功能"""
    logger.info("开始测试任务通知功能...")
    
    try:
        # 获取数据库会话
        db = SessionLocal()
        
        # 获取一个任务
        task = db.query(Task).filter(Task.is_deleted == False).first()
        if not task:
            logger.error("没有找到可用的任务进行测试")
            return
        
        logger.info(f"使用任务进行测试: ID={task.id}, 标题={task.title}")
        
        # 测试任务状态变更通知
        logger.info("测试任务状态变更通知...")
        await message_push_service.notify_task_status_changed(
            db, task, "pending", "in_progress"
        )
        
        # 测试任务分配通知
        if task.assignee_id:
            logger.info("测试任务分配通知...")
            await message_push_service.notify_task_assigned(
                db, task, task.assignee_id
            )
        
        # 测试任务创建通知
        logger.info("测试任务创建通知...")
        await message_push_service.notify_task_created(db, task)
        
        logger.info("任务通知测试完成")
        
    except Exception as e:
        logger.error(f"测试任务通知失败: {e}")
    finally:
        if 'db' in locals():
            db.close()

async def test_websocket_connection():
    """测试WebSocket连接"""
    logger.info("开始测试WebSocket连接...")
    
    try:
        from app.core.ws_manager import ws_manager
        
        # 获取连接数
        connection_count = len(ws_manager.active_connections)
        logger.info(f"当前WebSocket连接数: {connection_count}")
        
        # 获取用户连接
        user_connections = ws_manager.get_user_connections(1)  # 用户ID 1
        logger.info(f"用户1的连接数: {len(user_connections)}")
        
        # 发送测试消息
        test_message = {
            "type": "test_notification",
            "title": "测试通知",
            "content": "这是一个测试通知",
            "timestamp": "2025-06-27T13:50:00"
        }
        
        await ws_manager.send_personal_message(1, test_message)
        logger.info("已发送测试消息到用户1")
        
    except Exception as e:
        logger.error(f"测试WebSocket连接失败: {e}")

def main():
    """主函数"""
    logger.info("开始通知功能测试...")
    
    # 运行异步测试
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # 测试WebSocket连接
        loop.run_until_complete(test_websocket_connection())
        
        # 等待一下
        import time
        time.sleep(2)
        
        # 测试任务通知
        loop.run_until_complete(test_task_notification())
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
    finally:
        loop.close()
    
    logger.info("通知功能测试完成")

if __name__ == "__main__":
    main() 