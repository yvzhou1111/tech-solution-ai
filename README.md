# 技术方案生成AI应用

基于arXiv论文检索和豆包大模型的自动技术方案生成系统，支持前端对话式交互和后端定时任务处理。

## 项目概述

技术方案生成AI是一个基于最新学术研究和大语言模型的综合系统，可以根据用户输入的技术主题，自动搜索相关的arXiv论文，分析内容，并生成包含架构设计、技术细节和实施步骤的完整技术方案。系统支持中英文输入，并提供良好的可视化展示。

## 功能特点

- **arXiv论文检索**：自动搜索与技术主题相关的最新研究论文
- **智能文档解析**：支持PDF、网页等多种格式的文件内容提取
- **AI方案生成**：基于豆包系列大模型，生成详细可行的技术方案
- **流程图可视化**：使用Mermaid自动生成架构图和流程图
- **定时任务处理**：支持后台异步处理大型分析任务
- **多模型选择**：支持豆包思维专业版、豆包专业版和豆包轻量版
- **虚拟数据存储**：临时存储生成的技术方案，一天后自动删除
- **多语言支持**：支持中文输入，系统自动翻译为适合学术搜索的英文关键词

## 系统架构

```
┌─────────────┐       ┌─────────────┐       ┌───────────────┐
│  前端      │       │  后端API    │       │  arXiv API    │
│  (Vue.js)   │ ─────▶│  (FastAPI)  │ ─────▶│  (外部服务)   │
└─────────────┘       └─────────────┘       └───────────────┘
                          │                          │
                          ▼                          ▼
                     ┌─────────────┐          ┌───────────────┐
                     │  任务调度器  │          │   论文内容    │
                     │  (定时任务)  │          │   (PDF文件)   │
                     └─────────────┘          └───────────────┘
                          │                          │
                          └──────────────────────────┘
                                       │
                                       ▼
                                ┌─────────────┐
                                │  豆包API    │
                                │  (大模型)   │
                                └─────────────┘
                                       │
                                       ▼
                                ┌─────────────┐
                                │  技术方案   │
                                │  (结构化)   │
                                └─────────────┘
```

## 技术栈

### 前端

- **框架**：Vue.js 3
- **UI组件**：Bootstrap 5
- **HTTP客户端**：Axios
- **路由**：Vue Router
- **Markdown渲染**：Marked + Mermaid

### 后端

- **框架**：FastAPI (Python)
- **异步处理**：asyncio
- **PDF解析**：PyMuPDF
- **学术API**：arXiv.py
- **大模型API**：豆包API (方舟引擎)
- **数据存储**：虚拟文件数据库 (自动清理)

## 部署说明

### 系统要求

- Python 3.8+
- Node.js 12+
- npm 6+
- 互联网连接 (用于访问arXiv和豆包API)

### 后端部署

1. 进入后端目录

```bash
cd backend
```

2. 创建并激活虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

4. 配置环境变量

```bash
# 创建.env文件
echo VOLCANO_API_KEY=your_api_key > .env
```

5. 启动服务

```bash
# Windows
start.ps1

# Linux/Mac
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 前端部署

1. 进入前端目录

```bash
cd frontend
```

2. 安装依赖

```bash
npm install
```

3. 开发环境启动

```bash
npm run serve
```

4. 生产环境构建

```bash
npm run build
```

## API文档

启动后端服务后，可以通过以下URL访问API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

主要API路径包括：

- `POST /api/projects` - 创建新的技术方案生成项目
- `GET /api/projects/{id}` - 获取指定ID的项目详情
- `GET /api/projects` - 获取项目列表
- `POST /api/upload` - 上传文件进行分析
- `GET /api/papers/{id}/pdf` - 下载指定ID的论文PDF

## 任务设计文档

系统采用异步任务处理框架，主要流程如下：

1. **前端请求处理**：用户通过前端提交技术主题
2. **主题翻译**：如果输入为中文，系统使用豆包API将其翻译为英文关键词
3. **论文检索**：系统调用arXiv API搜索相关论文
4. **内容下载**：异步下载PDF论文到本地临时存储
5. **内容提取**：使用PyMuPDF从PDF中提取文本内容
6. **方案生成**：将论文内容和用户需求发送给豆包API生成技术方案
7. **结果返回**：将生成的技术方案和参考文献信息返回给前端
8. **数据清理**：一天后自动删除临时存储的PDF和项目数据

### 任务调度器

系统使用自定义任务调度器处理异步任务，主要特点：

- 支持异步协程任务提交
- 任务状态跟踪和错误处理
- 定时清理过期数据
- 内存和资源管理

## 使用说明

1. 打开前端页面 (默认: http://localhost:8080)
2. 输入项目标题和感兴趣的技术主题
3. (可选) 添加补充说明和自定义设置
4. 点击"生成技术方案"按钮
5. 等待系统处理 (1-3分钟)
6. 查看生成的技术方案，包含架构图和实施步骤
7. 可下载参考论文PDF或访问原始链接

## 开发调试

**后端开发**:
- API端点位于 `backend/app/routes.py`
- 配置文件在 `backend/app/config.py`
- 主要业务逻辑在 `backend/app/ai_service.py`

**前端开发**:
- 入口组件为 `frontend/src/App.vue`
- 页面组件在 `frontend/src/views/`
- API服务在 `frontend/src/services/api.js`

## 注意事项

- 系统需要有效的豆包API密钥 (方舟引擎)
- 技术方案生成可能需要几分钟时间
- 系统会临时存储下载的PDF，一天后自动删除
- arXiv API可能有访问频率限制

## 许可证

[MIT License](LICENSE)