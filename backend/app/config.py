import os

# 方舟引擎(Volcano Engine)API配置
VOLCANO_API_KEY = os.getenv("VOLCANO_API_KEY", "****")
VOLCANO_API_URL = os.getenv("VOLCANO_API_URL", "https://ark.cn-beijing.volces.com/api/v3/chat/completions")

# 方舟引擎豆包系列模型
VOLCANO_MODEL = "doubao-seed-1-6-250615"           
VOLCANO_DOUBAO_MODEL = "doubao-seed-1-6-250615"    
VOLCANO_DOUBAO_LITE = "doubao-seed-1-6-250615"     
VOLCANO_READER_MODEL = "doubao-seed-1-6-250615"   

# 当前选择的模型 - 主模型
CURRENT_MAIN_MODEL = "volcano"  # 可选 "volcano" 或 "deepseek"
# 当前选择的方舟模型
CURRENT_VOLCANO_MODEL = VOLCANO_MODEL  
# 模型选择允许从环境变量覆盖
CURRENT_VOLCANO_MODEL = os.getenv("VOLCANO_MODEL", CURRENT_VOLCANO_MODEL)
# 检查是否指定了使用豆包轻量版
if os.getenv("USE_DOUBAO_LITE", "").lower() in ("true", "1", "yes"):
    CURRENT_VOLCANO_MODEL = VOLCANO_DOUBAO_LITE
    print(f"从环境变量设置使用豆包轻量版: {VOLCANO_DOUBAO_LITE}")
elif os.getenv("USE_DOUBAO_PRO", "").lower() in ("true", "1", "yes"):
    CURRENT_VOLCANO_MODEL = VOLCANO_DOUBAO_MODEL
    print(f"从环境变量设置使用豆包专业版: {VOLCANO_DOUBAO_MODEL}")

# arXiv API配置
ARXIV_RESULTS_PER_QUERY = 5
ARXIV_SORT_BY = "relevance"  # 可选: relevance, lastUpdatedDate, submittedDate

# 本地文件存储
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
PDF_DIR = os.path.join(DATA_DIR, "pdfs")
os.makedirs(PDF_DIR, exist_ok=True)

# 数据库清理设置 (24小时)
DATA_RETENTION_HOURS = 24
