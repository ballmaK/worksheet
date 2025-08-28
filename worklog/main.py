from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from fastapi.responses import JSONResponse
from sqlalchemy import text
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 关闭SQLAlchemy的SQL日志
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.dialects').setLevel(logging.WARNING)

# 更严格的SQL日志控制
logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.engine.base.Engine').setLevel(logging.WARNING)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    default_response_class=JSONResponse,
    default_response_headers={"Content-Type": "application/json; charset=utf-8"}
)

# 设置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 测试数据库连接
logger.info("正在测试数据库连接...")
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        logger.info("数据库连接成功！")
except Exception as e:
    logger.error(f"数据库连接失败: {e}")
    raise

# 创建数据库表
logger.info("正在创建数据库表...")
Base.metadata.create_all(bind=engine)
logger.info("数据库表创建完成！")

# 注册路由
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to WorkLog Pro API"} 