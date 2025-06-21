# 技术方案生成AI后端启动脚本

# 检查是否存在虚拟环境，不存在则创建
if (-not (Test-Path ".\venv")) {
    Write-Host "正在创建虚拟环境..."
    python -m venv venv
}

# 激活虚拟环境
Write-Host "正在激活虚拟环境..."
.\venv\Scripts\Activate

# 安装依赖
Write-Host "正在安装依赖..."
pip install -r requirements.txt

# 设置模型类型(可选)
# 要使用豆包轻量版，取消下面的注释
# $env:USE_DOUBAO_LITE = "true"

# 要使用豆包专业版，取消下面的注释
# $env:USE_DOUBAO_PRO = "true"

# 启动服务
Write-Host "正在启动服务..."
python main.py