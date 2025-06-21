import asyncio
import threading
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Coroutine
from datetime import datetime
import uuid

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scheduler")

class TaskScheduler:
    def __init__(self):
        """初始化任务调度器"""
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()
        self.loop = asyncio.new_event_loop()
        
        # 启动调度器线程
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
    
    def _run_scheduler(self):
        """在独立线程中运行事件循环"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def submit_task(self, coroutine, task_id: Optional[str] = None) -> str:
        """提交异步任务到调度器"""
        with self.lock:
            if task_id is None:
                task_id = str(uuid.uuid4())
            
            # 创建任务记录
            task_record = {
                "id": task_id,
                "status": "pending",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "result": None,
                "error": None
            }
            
            self.tasks[task_id] = task_record
            
            # 创建任务并设置回调
            future = asyncio.run_coroutine_threadsafe(self._run_task(coroutine, task_id), self.loop)
            future.add_done_callback(lambda f: self._handle_task_result(task_id, f))
            
            return task_id
    
    async def _run_task(self, coroutine, task_id: str) -> Any:
        """执行异步任务并捕获异常"""
        try:
            # 更新任务状态为处理中
            self._update_task_status(task_id, "processing")
            
            # 执行协程任务
            result = await coroutine
            
            # 更新任务状态为已完成
            self._update_task_status(task_id, "completed", result=result)
            return result
        
        except Exception as e:
            # 记录错误并更新状态
            logger.error(f"任务 {task_id} 执行出错: {str(e)}")
            self._update_task_status(task_id, "failed", error=str(e))
            raise e
    
    def _handle_task_result(self, task_id: str, future):
        """处理任务完成后的结果"""
        try:
            # 获取任务结果
            future.result()
        except Exception as e:
            # 任务在_run_task中已经处理了异常，这里不需要再做额外处理
            pass
    
    def _update_task_status(self, task_id: str, status: str, result=None, error=None):
        """更新任务状态和结果"""
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id].update({
                    "status": status,
                    "updated_at": datetime.now().isoformat()
                })
                
                if result is not None:
                    self.tasks[task_id]["result"] = result
                
                if error is not None:
                    self.tasks[task_id]["error"] = error
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        with self.lock:
            return self.tasks.get(task_id)
    
    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """获取所有活动的任务"""
        with self.lock:
            return [task for task in self.tasks.values() if task["status"] in ("pending", "processing")]
    
    def schedule_periodic_task(self, coroutine_factory, interval_seconds: int, task_id_prefix: str = "periodic"):
        """调度定期任务"""
        async def periodic_runner():
            while True:
                try:
                    # 生成唯一的任务ID
                    task_id = f"{task_id_prefix}_{int(time.time())}"
                    
                    # 创建协程并提交任务
                    coroutine = coroutine_factory()
                    self.submit_task(coroutine, task_id)
                    
                    # 等待下一个间隔
                    await asyncio.sleep(interval_seconds)
                
                except Exception as e:
                    logger.error(f"定期任务调度出错: {str(e)}")
                    await asyncio.sleep(10)  # 出错时短暂等待后重试
        
        # 提交定期任务运行器
        asyncio.run_coroutine_threadsafe(periodic_runner(), self.loop)

# 创建全局任务调度器实例
scheduler = TaskScheduler() 