import json
import os
import time
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import threading
import uuid

from .config import DATA_DIR, DATA_RETENTION_HOURS

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)

# 虚拟数据库 - 使用文件系统实现简单持久化
class VirtualDatabase:
    def __init__(self):
        self.projects_dir = os.path.join(DATA_DIR, "projects")
        os.makedirs(self.projects_dir, exist_ok=True)
        
        # 启动清理线程
        self.cleanup_thread = threading.Thread(target=self._cleanup_scheduler, daemon=True)
        self.cleanup_thread.start()
    
    def _cleanup_scheduler(self):
        """定期清理过期数据的调度器"""
        while True:
            self.cleanup_old_data()
            # 每小时检查一次
            time.sleep(3600)
    
    def cleanup_old_data(self):
        """清理超过保留期的数据"""
        current_time = datetime.now()
        retention_limit = current_time - timedelta(hours=DATA_RETENTION_HOURS)
        
        try:
            for project_id in os.listdir(self.projects_dir):
                project_path = os.path.join(self.projects_dir, project_id)
                if not os.path.isdir(project_path):
                    continue
                    
                # 检查项目元数据
                meta_file = os.path.join(project_path, "metadata.json")
                if os.path.exists(meta_file):
                    with open(meta_file, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                    
                    # 检查创建时间
                    created_time = datetime.fromisoformat(metadata.get("created_at", "2000-01-01T00:00:00"))
                    if created_time < retention_limit:
                        print(f"清理过期项目: {project_id}, 创建时间: {created_time}")
                        shutil.rmtree(project_path)
        except Exception as e:
            print(f"清理过程发生错误: {e}")
    
    def create_project(self, title: str, topic: str, params: Dict[str, Any]) -> str:
        """创建新的项目"""
        project_id = str(uuid.uuid4())
        project_dir = os.path.join(self.projects_dir, project_id)
        os.makedirs(project_dir, exist_ok=True)
        
        # 创建项目元数据
        metadata = {
            "id": project_id,
            "title": title,
            "topic": topic,
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "params": params
        }
        
        with open(os.path.join(project_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return project_id
    
    def update_project(self, project_id: str, data: Dict[str, Any]):
        """更新项目数据"""
        project_dir = os.path.join(self.projects_dir, project_id)
        if not os.path.exists(project_dir):
            os.makedirs(project_dir, exist_ok=True)
        
        meta_file = os.path.join(project_dir, "metadata.json")
        if os.path.exists(meta_file):
            with open(meta_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        else:
            metadata = {"id": project_id, "created_at": datetime.now().isoformat()}
        
        # 更新元数据
        metadata.update(data)
        metadata["updated_at"] = datetime.now().isoformat()
        
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def save_project_result(self, project_id: str, result_data: Dict[str, Any]):
        """保存项目生成结果"""
        project_dir = os.path.join(self.projects_dir, project_id)
        if not os.path.exists(project_dir):
            os.makedirs(project_dir, exist_ok=True)
        
        # 保存结果数据
        with open(os.path.join(project_dir, "result.json"), "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        # 更新项目状态
        self.update_project(project_id, {"status": "completed"})
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """获取项目详情"""
        project_dir = os.path.join(self.projects_dir, project_id)
        meta_file = os.path.join(project_dir, "metadata.json")
        
        if not os.path.exists(meta_file):
            return None
        
        with open(meta_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        # 检查是否有结果文件
        result_file = os.path.join(project_dir, "result.json")
        if os.path.exists(result_file):
            with open(result_file, "r", encoding="utf-8") as f:
                result_data = json.load(f)
            metadata["result"] = result_data
        
        return metadata
    
    def list_projects(self, limit: int = 10) -> List[Dict[str, Any]]:
        """列出最近的项目"""
        if not os.path.exists(self.projects_dir):
            return []
        
        projects = []
        for project_id in os.listdir(self.projects_dir):
            project_dir = os.path.join(self.projects_dir, project_id)
            meta_file = os.path.join(project_dir, "metadata.json")
            
            if os.path.exists(meta_file):
                with open(meta_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                projects.append(metadata)
        
        # 按创建时间排序
        projects.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return projects[:limit]
    
    def save_file(self, project_id: str, filename: str, content: bytes) -> str:
        """保存上传的文件"""
        project_dir = os.path.join(self.projects_dir, project_id)
        files_dir = os.path.join(project_dir, "files")
        os.makedirs(files_dir, exist_ok=True)
        
        file_path = os.path.join(files_dir, filename)
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 返回相对路径
        return os.path.join("files", filename)

# 创建虚拟数据库实例
db = VirtualDatabase() 