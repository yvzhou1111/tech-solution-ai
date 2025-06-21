import uvicorn
import os
import sys

# 添加当前目录到模块搜索路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == "__main__":
    # 从环境变量获取配置或使用默认值
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    # 启动服务器
    print(f"启动服务器: http://{host}:{port}")
    uvicorn.run("app:app", host=host, port=port, reload=True) 