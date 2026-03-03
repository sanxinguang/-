# main.py

from fastapi import FastAPI
import logging

from app.db.session import Base, engine 
from app.api.endpoints import router as api_router

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """安全地初始化数据库"""
    try:
        logger.info("正在初始化数据库...")
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功！")
        return True
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        return False

# 创建FastAPI应用实例
app = FastAPI(title="Comment Crawler API", version="1.0.0")

app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    if not init_database():
        logger.warning("数据库初始化失败，但应用将继续运行")

@app.get("/")
def root():
    return {
        "message": "Welcome to the Comment Crawler API!",
        "docs": "/docs",
        "api": "/api/v1"
    }

@app.get("/health")
def health_check():
    """健康检查端点"""
    return {"status": "healthy", "message": "API is running"}