import re
import os
import json
import time
import arxiv
import httpx
import asyncio
import tempfile
from typing import Dict, List, Optional, Any, Tuple
import aiohttp
from urllib.request import urlretrieve
import logging

from .config import (
    VOLCANO_API_KEY, 
    VOLCANO_API_URL,
    CURRENT_VOLCANO_MODEL, 
    ARXIV_RESULTS_PER_QUERY, 
    ARXIV_SORT_BY,
    PDF_DIR
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_service")

async def translate_to_english(topic: str) -> str:
    """将中文主题翻译为英文关键词"""
    if not re.search(r'[\u4e00-\u9fff]', topic):
        return topic  # 如果不包含中文，直接返回
    
    logger.info(f"翻译主题: {topic}")
    
    # 构造翻译请求
    data = {
        "model": CURRENT_VOLCANO_MODEL,
        "messages": [
            {
                "role": "system", 
                "content": "你是一位专业的翻译助手。请将中文技术主题翻译为适合英文学术搜索的关键词。只需要返回翻译结果，不要有任何额外的解释或装饰。"
            },
            {
                "role": "user",
                "content": f"请将以下技术主题翻译为适合在arXiv等学术搜索引擎使用的英文关键词:\n\n{topic}"
            }
        ],
        "temperature": 0.3,  # 降低随机性以获得更稳定的翻译
    }
    
    try:
        # 调用豆包API进行翻译
        async with httpx.AsyncClient() as client:
            response = await client.post(
                VOLCANO_API_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {VOLCANO_API_KEY}"
                },
                json=data,
                timeout=30.0
            )
            
            response_data = response.json()
            if "choices" in response_data and len(response_data["choices"]) > 0:
                translation = response_data["choices"][0]["message"]["content"].strip()
                logger.info(f"翻译结果: {translation}")
                return translation
            else:
                logger.error(f"翻译失败: {response_data}")
                return topic  # 失败时返回原始主题
    except Exception as e:
        logger.error(f"翻译过程出错: {str(e)}")
        return topic  # 出错时返回原始主题

async def search_arxiv_papers(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """搜索arXiv相关论文"""
    logger.info(f"搜索arXiv论文: {query}, 最大结果: {max_results}")
    
    try:
        # 使用arxiv客户端搜索论文
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=ARXIV_SORT_BY
        )
        
        papers = []
        
        # 使用同步函数处理结果
        def process_results():
            results = list(search.results())
            for result in results:
                # 从arXiv结果中提取需要的信息
                paper_info = {
                    "id": result.entry_id.split("/")[-1],
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "summary": result.summary.replace("\n", " "),
                    "published": result.published.isoformat(),
                    "pdf_url": result.pdf_url,
                    "local_path": None,
                    "content_extracted": False
                }
                papers.append(paper_info)
            return papers
        
        # 在事件循环内执行同步函数
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, process_results)
        
        logger.info(f"找到 {len(papers)} 篇论文")
        return papers
    except Exception as e:
        logger.error(f"搜索arXiv论文时出错: {str(e)}")
        return []

async def download_papers(papers: List[Dict[str, Any]], timeout: int = 30) -> List[Dict[str, Any]]:
    """下载论文PDF并更新本地路径"""
    logger.info(f"开始下载 {len(papers)} 篇论文")
    
    for i, paper in enumerate(papers):
        try:
            # 构建PDF文件路径
            filename = f"{paper['id']}.pdf"
            local_path = os.path.join(PDF_DIR, filename)
            
            # 如果PDF已经存在，跳过下载
            if os.path.exists(local_path):
                paper["local_path"] = local_path
                logger.info(f"论文PDF已存在: {filename}")
                continue
            
            # 下载PDF
            logger.info(f"下载论文 {i+1}/{len(papers)}: {paper['title']}")
            
            # 使用urlretrieve下载PDF，添加超时控制
            async def download_with_timeout():
                try:
                    # 使用httpx替代urlretrieve，以便更好地控制超时
                    async with httpx.AsyncClient(timeout=timeout) as client:
                        response = await client.get(paper["pdf_url"])
                        if response.status_code == 200:
                            with open(local_path, "wb") as f:
                                f.write(response.content)
                            return local_path
                        else:
                            logger.warning(f"下载论文失败，状态码: {response.status_code}")
                            return None
                except Exception as e:
                    logger.error(f"下载过程出错: {str(e)}")
                    return None
            
            # 执行下载，设置超时
            try:
                result_path = await asyncio.wait_for(download_with_timeout(), timeout=timeout)
                if result_path:
                    paper["local_path"] = result_path
                    logger.info(f"成功下载论文: {filename}")
                else:
                    logger.warning(f"论文 {paper['id']} 下载失败，跳过")
            except asyncio.TimeoutError:
                logger.warning(f"下载论文 {paper['id']} 超时，跳过")
            
            # 避免同时发起太多请求
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"下载论文 {paper['id']} 时出错: {str(e)}")
    
    # 过滤掉没有成功下载的论文
    valid_papers = [p for p in papers if p.get("local_path")]
    if len(valid_papers) < len(papers):
        logger.warning(f"部分论文下载失败，原始数量: {len(papers)}，有效数量: {len(valid_papers)}")
    
    # 确保至少有一篇论文可用
    if not valid_papers and papers:
        # 如果所有下载都失败，至少保留一篇论文的元数据
        logger.warning("所有论文下载失败，但仍将使用元数据继续处理")
        valid_papers = [papers[0]]
    
    return valid_papers

async def extract_paper_content(paper: Dict[str, Any], max_pages: int = 5) -> str:
    """提取PDF论文内容"""
    # 如果没有本地文件路径，仅使用摘要信息
    if not paper.get("local_path"):
        logger.warning(f"无法提取论文内容，使用摘要代替: {paper.get('id')}")
        return paper.get('summary', '')
    
    if not os.path.exists(paper["local_path"]):
        logger.warning(f"论文文件不存在，使用摘要代替: {paper.get('id')}")
        return paper.get('summary', '')
    
    try:
        # 定义同步提取函数
        def extract_pdf_content(file_path, max_pages):
            try:
                import fitz  # PyMuPDF
                
                logger.info(f"提取论文内容: {paper['title']}")
                doc = fitz.open(file_path)
                
                # 只提取前几页内容以节省token
                content = ""
                for i in range(min(max_pages, len(doc))):
                    page = doc[i]
                    content += page.get_text()
                
                return content
            except Exception as e:
                logger.error(f"PDF内容提取出错: {str(e)}")
                return paper.get('summary', '')
        
        # 在事件循环中执行PDF提取，设置超时
        try:
            loop = asyncio.get_event_loop()
            content = await asyncio.wait_for(
                loop.run_in_executor(None, lambda: extract_pdf_content(paper["local_path"], max_pages)),
                timeout=15
            )
            # 标记为已提取
            paper["content_extracted"] = True
            return content
        except asyncio.TimeoutError:
            logger.warning(f"提取论文 {paper['id']} 内容超时，使用摘要代替")
            return paper.get('summary', '')
    except Exception as e:
        logger.error(f"提取论文内容时出错: {str(e)}")
        return paper.get('summary', '')

async def generate_technical_proposal(
    topic: str, 
    papers: List[Dict[str, Any]],
    extracted_contents: List[str] = None,
    model_type: str = "default",
    max_tokens: int = 4000
) -> Dict[str, Any]:
    """生成技术方案"""
    logger.info(f"生成技术方案: {topic}, 使用模型类型: {model_type}")
    
    # 构建提示词
    system_prompt = """你是一位专业的技术顾问，擅长基于学术论文生成详细的技术方案。
你将分析提供的论文信息，生成一份全面的技术方案，包括：
1. 架构设计和系统组件
2. 实施步骤和关键算法
3. 所需资源和技术栈
4. 潜在挑战和解决方案

请以Markdown格式输出，确保方案具有可执行性和技术深度。使用表格展示比较信息，使用列表说明有序步骤。
如果可能，添加一个用Mermaid语法表示的系统架构图。"""

    # 如果是中文主题，使用中文系统提示
    if re.search(r'[\u4e00-\u9fff]', topic):
        system_prompt = """你是一位专业的技术顾问，擅长基于学术论文生成详细的技术方案。
你将分析提供的论文信息，生成一份全面的技术方案，包括：
1. 架构设计和系统组件
2. 实施步骤和关键算法
3. 所需资源和技术栈
4. 潜在挑战和解决方案

请以Markdown格式输出，确保方案具有可执行性和技术深度。使用表格展示比较信息，使用列表说明有序步骤。
如果可能，添加一个用Mermaid语法表示的系统架构图。"""
    
    # 构建论文信息
    papers_info = []
    for i, paper in enumerate(papers):
        paper_info = f"论文 {i+1}:\n"
        paper_info += f"标题: {paper['title']}\n"
        paper_info += f"作者: {', '.join(paper['authors'])}\n"
        paper_info += f"摘要: {paper['summary']}\n"
        if extracted_contents and i < len(extracted_contents) and extracted_contents[i]:
            paper_info += f"内容摘录: {extracted_contents[i][:3000]}...\n"  # 限制内容长度
        papers_info.append(paper_info)
    
    papers_text = "\n\n".join(papers_info)
    
    # 构建用户提示词
    user_prompt = f"""请基于以下研究主题和相关论文，生成一份详细的技术方案：

研究主题: {topic}

相关论文信息:
{papers_text}

请在方案中包括：
1. 详细的架构设计（使用Mermaid图表）
2. 核心技术组件和它们的交互
3. 实施路径和时间线
4. 所需的技术资源和依赖
5. 参考资料和进一步阅读建议

方案应当既有理论基础，又具备实用性和可执行性。"""
    
    # 构造API请求数据
    data = {
        "model": CURRENT_VOLCANO_MODEL,
        "messages": [
            {
                "role": "system", 
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,  # 控制生成的随机性
        "top_p": 0.9,        # 使用nucleus采样
        "seed": 1234         # 设置固定种子，提高一致性
    }
    
    try:
        # 调用豆包API生成技术方案
        async with httpx.AsyncClient() as client:
            response = await client.post(
                VOLCANO_API_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {VOLCANO_API_KEY}"
                },
                json=data,
                timeout=120.0  # 生成复杂内容，增加超时时间
            )
            
            response_data = response.json()
            if "choices" in response_data and len(response_data["choices"]) > 0:
                proposal = response_data["choices"][0]["message"]["content"]
                
                # 提取架构图（如果有）
                architecture_diagram = None
                diagram_match = re.search(r"```mermaid\s+([\s\S]+?)\s+```", proposal)
                if diagram_match:
                    architecture_diagram = diagram_match.group(1)
                
                # 提取实施步骤
                steps = []
                steps_section = re.search(r"## 实施步骤[\s\S]+?(?=##|$)", proposal)
                if steps_section:
                    steps_text = steps_section.group(0)
                    step_matches = re.findall(r"\d+\.\s+(.+?)(?=\n\d+\.|\n##|\Z)", steps_text)
                    steps = [{"step": i+1, "description": step.strip()} for i, step in enumerate(step_matches)]
                
                # 提取所需资源
                resources = []
                resources_section = re.search(r"## 所需资源[\s\S]+?(?=##|$)", proposal)
                if resources_section:
                    resources_text = resources_section.group(0)
                    resource_matches = re.findall(r"-\s+(.+?)(?=\n-|\n##|\Z)", resources_text)
                    resources = [{"type": "resource", "description": res.strip()} for res in resource_matches]
                
                # 构建结果
                result = {
                    "technical_proposal": proposal,
                    "architecture_diagram": architecture_diagram,
                    "implementation_steps": steps,
                    "resources_needed": resources,
                    "references": [
                        {
                            "id": p["id"],
                            "title": p["title"],
                            "authors": p["authors"],
                            "summary": p["summary"],
                            "published": p["published"],
                            "pdf_url": p["pdf_url"],
                            "local_path": p.get("local_path")
                        } for p in papers
                    ]
                }
                
                return result
            else:
                logger.error(f"生成技术方案失败: {response_data}")
                return {"error": "生成技术方案失败", "details": response_data}
    except Exception as e:
        logger.error(f"生成技术方案时出错: {str(e)}")
        return {"error": str(e)}

async def process_uploaded_file(file_path: str, file_type: str) -> str:
    """处理上传的文件，提取内容"""
    logger.info(f"处理上传的文件: {file_path}, 类型: {file_type}")
    
    try:
        content = ""
        
        # 根据文件类型使用不同的处理方法
        if file_type.endswith('.pdf'):
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            for page in doc:
                content += page.get_text()
        
        elif file_type.endswith(('.txt', '.md')):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        
        elif file_type.endswith(('.docx', '.doc')):
            import docx
            doc = docx.Document(file_path)
            content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        
        # 可以继续添加对其他文件类型的支持
        
        return content
    except Exception as e:
        logger.error(f"处理上传文件时出错: {str(e)}")
        return ""

async def analyze_web_content(url: str) -> str:
    """使用LinkReader插件分析网页内容"""
    logger.info(f"分析网页内容: {url}")
    
    # 构造LinkReader请求
    data = {
        "model": CURRENT_VOLCANO_MODEL,
        "messages": [
            {
                "role": "user",
                "content": f"请分析并总结这个URL的内容: {url}"
            }
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "LinkReader",
                    "description": "解析URL内容，支持网页、PDF等格式",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "urls": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "要解析的URL列表"
                            }
                        },
                        "required": ["urls"]
                    }
                }
            }
        ]
    }
    
    try:
        # 调用豆包API进行网页内容分析
        async with httpx.AsyncClient() as client:
            response = await client.post(
                VOLCANO_API_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {VOLCANO_API_KEY}"
                },
                json=data,
                timeout=60.0
            )
            
            response_data = response.json()
            if "choices" in response_data and len(response_data["choices"]) > 0:
                result = response_data["choices"][0]["message"]["content"]
                return result
            else:
                logger.error(f"网页内容分析失败: {response_data}")
                return ""
    except Exception as e:
        logger.error(f"网页内容分析出错: {str(e)}")
        return ""