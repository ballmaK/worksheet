from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.db.base_class import Base
from app.core.config import settings
import logging
import os
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# 获取数据库URL
database_url = settings.SQLALCHEMY_DATABASE_URL

# 打印调试信息
logger.info(f"Database URL: {database_url}")

if settings.USE_SQLITE:
    logger.info("使用 SQLite 数据库")
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    logger.info("使用 MySQL 数据库")
    # 使用更保守的连接池配置
    engine = create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=5,  # 减小连接池大小
        max_overflow=10,  # 减小最大溢出连接数
        pool_pre_ping=True,  # 连接前ping检查
        pool_recycle=1800,  # 30分钟回收连接
        pool_timeout=30,  # 连接超时时间
        connect_args={
            "charset": "utf8mb4",
            "read_timeout": 60,
            "write_timeout": 60,
            "connect_timeout": 60,
            "autocommit": False,
            "sql_mode": "STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO"
        },
        echo=False
    )

    # 添加连接事件监听器
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if not settings.USE_SQLITE:
            # MySQL连接配置
            cursor = dbapi_connection.cursor()
            cursor.execute("SET SESSION sql_mode='STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'")
            cursor.execute("SET SESSION wait_timeout=28800")
            cursor.execute("SET SESSION interactive_timeout=28800")
            cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 依赖项
def get_db():
    """
    获取数据库会话，带有完整的错误处理
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"数据库会话错误: {e}")
        try:
            db.rollback()
        except Exception as rollback_error:
            logger.error(f"回滚失败: {rollback_error}")
        raise
    finally:
        try:
            db.close()
        except Exception as e:
            logger.error(f"关闭数据库会话时出错: {e}")

@contextmanager
def get_db_session():
    """
    上下文管理器版本的数据库会话
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"数据库会话错误: {e}")
        try:
            db.rollback()
        except Exception as rollback_error:
            logger.error(f"回滚失败: {rollback_error}")
        raise
    finally:
        try:
            db.close()
        except Exception as e:
            logger.error(f"关闭数据库会话时出错: {e}")

def init_db():
    """
    初始化数据库
    """
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise 