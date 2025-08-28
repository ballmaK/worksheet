#!/usr/bin/env python3
"""
定时提醒运行脚本
用于定期发送各种提醒通知
"""

import asyncio
import logging
import time
from datetime import datetime

from app.core.reminder_service import reminder_service

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """主函数"""
    logger.info("启动定时提醒服务...")
    
    while True:
        try:
            # 运行所有提醒
            await reminder_service.run_all_reminders()
            
            # 等待1小时后再运行
            logger.info("提醒运行完成，等待1小时后再次运行...")
            await asyncio.sleep(3600)  # 1小时 = 3600秒
            
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在停止服务...")
            break
        except Exception as e:
            logger.error(f"运行提醒时发生错误: {e}")
            # 等待5分钟后重试
            await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(main()) 