from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile, Form, Depends, Query
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import os
import shutil
from typing import Dict, List, Optional, Any
import logging
import time

from .models import ProjectRequest, Project, ProjectStatus, ErrorResponse
from .database import db
from .scheduler import scheduler
from .ai_service import (
    translate_to_english,
    search_arxiv_papers,
    download_papers,
    extract_paper_content,
    generate_technical_proposal,
    process_uploaded_file,
    analyze_web_content
)
from .config import PDF_DIR

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("routes")

# 创建FastAPI应用
app = FastAPI(title="技术方案生成AI")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "message": "服务正常运行"}

@app.post("/api/projects", response_model=Dict[str, Any])
async def create_project(project_request: ProjectRequest):
    """创建新的技术方案项目"""
    try:
        # 创建项目记录
        project_id = db.create_project(
            title=project_request.title,
            topic=project_request.topic,
            params=project_request.dict()
        )
        
        # 提交后台任务
        task_id = scheduler.submit_task(
            process_project(project_id, project_request)
        )
        
        # 更新项目状态为处理中
        db.update_project(project_id, {
            "status": "processing",
            "task_id": task_id
        })
        
        return {
            "status": "success",
            "message": "项目创建成功，正在处理中",
            "project_id": project_id,
            "task_id": task_id
        }
    except Exception as e:
        logger.error(f"创建项目时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建项目时出错: {str(e)}")

async def process_project(project_id: str, request: ProjectRequest):
    """处理项目的后台任务"""
    try:
        # 1. 如果是中文主题，翻译为英文关键词
        topic = request.topic
        translated_topic = None
        
        if any('\u4e00' <= c <= '\u9fff' for c in topic):
            translated_topic = await translate_to_english(topic)
            search_query = translated_topic
            # 更新项目状态
            db.update_project(project_id, {
                "translated_topic": translated_topic,
                "status_message": "已翻译主题，正在搜索相关论文"
            })
        else:
            search_query = topic
            db.update_project(project_id, {
                "status_message": "正在搜索相关论文"
            })
        
        # 2. 搜索arXiv论文
        max_papers = request.max_papers if request.max_papers else 5
        papers = await search_arxiv_papers(search_query, max_papers)
        
        # 即使没有找到论文，也尝试继续处理
        if not papers:
            logger.warning(f"未找到与主题 '{topic}' 相关的论文，将尝试生成基本方案")
            # 创建一个基本的论文结构
            papers = [{
                "id": "default_paper",
                "title": f"关于 {topic} 的技术方案",
                "authors": ["系统生成"],
                "summary": f"由于未找到相关学术论文，系统将基于主题 '{topic}' 生成基本技术方案。",
                "published": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "pdf_url": None,
                "local_path": None,
                "content_extracted": False
            }]
        
        # 更新项目状态
        db.update_project(project_id, {
            "papers": papers,
            "status_message": "正在下载论文PDF"
        })
        
        # 3. 下载论文PDF（添加超时参数）
        papers = await download_papers(papers, timeout=60)
        db.update_project(project_id, {
            "papers": papers,
            "status_message": "正在提取论文内容"
        })
        
        # 4. 提取论文内容
        extracted_contents = []
        for paper in papers:
            content = await extract_paper_content(paper)
            extracted_contents.append(content)
        
        # 更新项目状态
        db.update_project(project_id, {
            "status_message": "正在生成技术方案"
        })
        
        # 5. 生成技术方案
        result = await generate_technical_proposal(
            topic=topic,
            papers=papers,
            extracted_contents=extracted_contents,
            model_type=request.model_type,
            max_tokens=4000
        )
        
        if "error" in result:
            # 处理生成失败的情况
            db.update_project(project_id, {
                "status": "failed",
                "error": result["error"]
            })
            return {"error": result["error"]}
        
        # 如果有翻译过的主题，添加到结果中
        if translated_topic:
            result["translated_topic"] = translated_topic
        
        # 6. 保存项目结果
        db.save_project_result(project_id, result)
        
        # 7. 更新项目状态为已完成
        db.update_project(project_id, {
            "status": "completed",
            "status_message": "技术方案生成完成"
        })
        
        return {"success": True, "project_id": project_id}
    
    except Exception as e:
        logger.error(f"处理项目 {project_id} 时出错: {str(e)}")
        # 更新项目状态为失败
        db.update_project(project_id, {
            "status": "failed",
            "error": str(e),
            "status_message": f"处理失败: {str(e)[:100]}" # 限制错误消息长度
        })
        return {"error": str(e)}

@app.get("/api/projects/{project_id}", response_model=Optional[Project])
async def get_project(project_id: str):
    """获取项目详情"""
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"找不到项目ID: {project_id}")
    return project

@app.get("/api/projects", response_model=List[Project])
async def list_projects(limit: int = Query(10, ge=1, le=100)):
    """列出最近的项目"""
    return db.list_projects(limit)

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), project_id: Optional[str] = Form(None)):
    """上传文件接口"""
    try:
        # 创建临时文件保存上传的内容
        file_location = os.path.join(PDF_DIR, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 如果提供了项目ID，将文件关联到项目
        if project_id:
            relative_path = db.save_file(project_id, file.filename, await file.read())
            db.update_project(project_id, {
                "files": db.get_project(project_id).get("files", []) + [
                    {
                        "filename": file.filename,
                        "path": relative_path,
                        "content_type": file.content_type
                    }
                ]
            })
        
        return {
            "status": "success", 
            "filename": file.filename,
            "file_path": file_location,
            "content_type": file.content_type
        }
    except Exception as e:
        logger.error(f"文件上传出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件上传出错: {str(e)}")

@app.post("/api/analyze-url")
async def analyze_url(url: str = Form(...)):
    """分析URL内容"""
    try:
        result = await analyze_web_content(url)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"URL分析出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"URL分析出错: {str(e)}")

@app.get("/api/papers/{paper_id}/pdf")
async def get_paper_pdf(paper_id: str):
    """获取论文PDF文件"""
    file_path = os.path.join(PDF_DIR, f"{paper_id}.pdf")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="论文PDF不存在")
    
    return StreamingResponse(
        open(file_path, "rb"),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={paper_id}.pdf"}
    )

# 定期清理任务 - 每天运行一次
@app.on_event("startup")
async def schedule_cleanup():
    """启动时调度定期清理任务"""
    def cleanup_task_factory():
        async def cleanup():
            logger.info("执行定期数据清理任务")
            db.cleanup_old_data()
            return {"status": "success"}
        return cleanup()
    
    # 每86400秒(24小时)运行一次清理任务
    scheduler.schedule_periodic_task(cleanup_task_factory, 86400, "cleanup")
    logger.info("已调度定期清理任务") 