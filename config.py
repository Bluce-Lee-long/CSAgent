import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 阿里云通义千问配置
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
    DASHSCOPE_MODEL = "qwen-turbo"
    
    # 向量数据库配置
    VECTOR_DB_PATH = "vector_db"
    
    # 文档处理配置 - 基于PDF分析优化
    PDF_PATH = "线下店文档.pdf"
    CHUNK_SIZE = 500      # 优化：减少chunk大小，降低token消耗
    CHUNK_OVERLAP = 120    # 优化：减少重叠比例，提高响应速度
    
    # 系统提示词
    SYSTEM_PROMPT = """您是教培管家，专注线下店文档咨询。

核心能力：
- 陪跑教练：0-1线下店全流程指导
- 财务管家：财务指标解读与规划
- 急诊医生：风险场景解决方案
- 情感链接：创业者压力管理与执行指导

要求：
- 仅回答线下店文档相关问题
- 专业且温暖，提供可执行建议
- 无关问题提示"仅支持该文档范围咨询"
- 回答中不要有"文档中提到" "第一章中"这些表述

基于文档内容，专业温暖地回答用户问题。"""

