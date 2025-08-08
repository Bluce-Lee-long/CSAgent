from typing import List, Dict, Tuple
from pdf_processor import PDFProcessor
from vector_store import VectorStore
from llm_client import LLMClient
from config import Config
from quick_action_cache import QuickActionCache

class IntelligentAgent:
    def __init__(self):
        self.vector_store = VectorStore()
        self.llm_client = LLMClient()
        self.conversation_history = []
        self.cache = QuickActionCache()  # 初始化缓存管理器
        
        # 初始化知识库
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """初始化知识库"""
        # 尝试加载现有向量数据库
        if not self.vector_store.load():
            print("正在构建新的知识库...")
            self._build_knowledge_base()
    
    def _build_knowledge_base(self):
        """构建知识库"""
        # 处理PDF文档
        processor = PDFProcessor(Config.PDF_PATH)
        chunks = processor.process_document()
        
        if chunks:
            # 添加到向量数据库
            self.vector_store.add_chunks(chunks)
            self.vector_store.save()
            print("知识库构建完成")
        else:
            print("无法处理PDF文档，知识库构建失败")
    
    def query(self, user_input: str) -> str:
        """处理用户查询"""
        # 检查查询相关性
        if not self.llm_client.is_relevant_query(user_input):
            return "抱歉，我仅支持线下店文档范围内的咨询。请询问关于教培机构运营、财务、风险处理等相关问题。"
        
        # 搜索相关文档
        relevant_chunks = self.vector_store.search(user_input, top_k=5)  # 减少检索数量，提高响应速度
        
        # 生成回答
        response = self.llm_client.generate_response(
            user_input, 
            relevant_chunks, 
            self.conversation_history
        )
        
        # 更新对话历史
        self.conversation_history.append({
            'role': 'user',
            'content': user_input
        })
        self.conversation_history.append({
            'role': 'assistant',
            'content': response
        })
        
        # 保持对话历史在合理范围内
        if len(self.conversation_history) > 6:  # 减少历史记录数量，提高响应速度
            self.conversation_history = self.conversation_history[-6:]
        
        return response
    
    def query_with_cache(self, user_input: str) -> str:
        """处理用户查询（带缓存功能）"""
        import time
        
        # 首先检查缓存
        cached_response = self.cache.get_cached_response(user_input)
        if cached_response:
            print(f"📋 使用缓存响应: {user_input[:50]}...")
            # 停5秒后返回缓存响应
            time.sleep(5)
            return cached_response
        
        # 如果没有缓存，调用大模型生成
        print(f"🤖 调用大模型生成: {user_input[:50]}...")
        response = self.query(user_input)
        
        # 缓存响应结果
        self.cache.cache_response(user_input, response)
        
        return response
    
    def get_quick_actions(self) -> List[Dict]:
        """获取快捷操作 - 基于线下店文档关键词优化"""
        return [
            {
                'title': '选址评估指南',
                'description': '线下店选址标准与评估方法',
                'query': '请说明线下店选址的具体标准、评估方法和注意事项，包括位置选择、人流分析、成本考虑、竞争环境评估等关键要素。'
            },
            {
                'title': '成本控制策略',
                'description': '租金、人力等成本控制标准',
                'query': '请说明线下店成本控制的具体策略，包括租金比例控制（建议不超过15%）、人力成本管理（建议不超过40%）、运营费用优化等各项成本的最佳控制标准。'
            },
            {
                'title': '运营管理体系',
                'description': '日常运营管理流程与标准',
                'query': '请说明线下店的运营管理体系，包括日常管理流程、标准化操作规范、效率提升方法、质量控制体系、学员管理流程等核心运营要素。'
            },
            {
                'title': '财务管理规划',
                'description': '现金流预测与财务指标',
                'query': '请说明线下店的财务管理规划，包括现金流预测方法、财务指标监控体系、预警线设置标准、收入结构分析、支出控制策略等关键财务管理要素。'
            },
            {
                'title': '盈利模式分析',
                'description': '教培机构盈利模式与策略',
                'query': '请分析线下教培机构的盈利模式，包括收入来源结构分析、利润结构优化、定价策略制定、成本控制方法、规模效应利用等盈利策略要素。'
            },
            {
                'title': '装修设计方案',
                'description': '线下店装修设计要点',
                'query': '请说明线下店的装修设计方案，包括空间布局规划、装修标准制定、成本控制策略、安全规范要求、教学环境设计等装修设计要素。'
            },
            {
                'title': '师资培训体系',
                'description': '教师培训与管理方案',
                'query': '请说明线下店的师资培训体系，包括教师招聘标准、培训方案设计、管理机制建立、绩效考核体系、职业发展规划等师资管理要素。'
            },
            {
                'title': '营销推广策略',
                'description': '招生营销与品牌推广',
                'query': '请说明线下店的营销推广策略，包括招生方法设计、品牌推广策略、市场拓展计划、客户获取渠道、营销活动策划等营销推广要素。'
            },
            {
                'title': '客户服务标准',
                'description': '学员服务与满意度管理',
                'query': '请说明线下店的客户服务标准，包括学员服务流程设计、满意度管理体系、投诉处理机制、客户关系维护、服务质量监控等客户服务要素。'
            },
            {
                'title': '课程设计体系',
                'description': '课程开发与教学设计',
                'query': '请说明线下店的课程设计体系，包括课程开发流程、教学设计方法、质量保证体系、课程评估机制、教学资源管理等课程设计要素。'
            },
            {
                'title': '团队建设方案',
                'description': '团队管理与文化建设',
                'query': '请说明线下店的团队建设方案，包括团队管理方法、文化建设策略、激励机制设计、沟通机制建立、团队协作模式等团队建设要素。'
            },
            {
                'title': '风险控制体系',
                'description': '风险识别与应对策略',
                'query': '请说明线下店的风险控制体系，包括风险识别方法、预防措施制定、应对策略设计、应急预案建立、风险监控机制等风险控制要素。'
            },
            {
                'title': '多店复制模型',
                'description': '从单店到连锁的扩张策略',
                'query': '请说明线下店的多店复制模型，包括扩张策略制定、标准化体系建设、管理复制方法、人才培养机制、品牌统一管理等多店复制要素。'
            }
        ]
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []

if __name__ == "__main__":
    # 测试智能客服Agent
    agent = IntelligentAgent()
    
    # 测试查询
    test_queries = [
        "线下店选址有什么注意事项？",
        "如何控制运营成本？",
        "今天天气怎么样？"  # 无关查询
    ]
    
    for query in test_queries:
        print(f"\n用户: {query}")
        response = agent.query(query)
        print(f"助手: {response}")

