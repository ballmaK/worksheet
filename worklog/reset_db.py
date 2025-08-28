from sqlalchemy import create_engine, text
from app.core.config import settings

def reset_database():
    # 创建不带数据库名的连接
    base_url = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}"
    engine = create_engine(base_url)
    
    with engine.connect() as conn:
        # 删除数据库（如果存在）
        conn.execute(text("DROP DATABASE IF EXISTS worklog"))
        # 创建新数据库
        conn.execute(text("CREATE DATABASE worklog"))
        conn.commit()

if __name__ == "__main__":
    reset_database() 