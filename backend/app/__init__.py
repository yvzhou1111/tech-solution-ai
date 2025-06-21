from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import logging

from .routes import app

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 静态文件目录
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)

# 模板目录
templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=templates_dir)

# 挂载静态文件
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 添加根路由
@app.get("/")
async def root():
    """重定向到文档页面"""
    return {"status": "ok", "message": "API服务运行正常，请访问 /docs 查看API文档"}

# 导出应用
__all__ = ["app"] 