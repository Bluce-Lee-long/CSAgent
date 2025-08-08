import dashscope
from dashscope import Generation
from typing import List, Dict
from config import Config
import hashlib
import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer

class LLMClient:
    def __init__(self):
        dashscope.api_key = Config.DASHSCOPE_API_KEY
        self.model = Config.DASHSCOPE_MODEL
        self.relevance_cache = {}  # 相关性判断缓存
        self.cache_file = "relevance_cache.json"
        self._load_relevance_cache()
        
        # 初始化向量模型用于相似度计算
        try:
            self.embedding_model = SentenceTransformer('shibing624/text2vec-base-chinese')
            self.relevant_domain_queries = [
                "线下店选址标准",
                "教培机构运营管理",
                "线下店成本控制",
                "教培机构财务管理",
                "线下店装修设计",
                "教培机构师资培训",
                "线下店营销推广",
                "教培机构客户服务",
                "线下店风险控制",
                "教培机构课程设计",
                "线下店团队建设",
                "教培机构多店复制"
            ]
            self.domain_embeddings = self.embedding_model.encode(self.relevant_domain_queries)
        except Exception:
            self.embedding_model = None
            self.domain_embeddings = None
    
    def _load_relevance_cache(self):
        """加载相关性判断缓存"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.relevance_cache = json.load(f)
        except Exception:
            self.relevance_cache = {}
    
    def _save_relevance_cache(self):
        """保存相关性判断缓存"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                # 把python对象转换成json对象生成一个fp的文件流
                json.dump(self.relevance_cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def _get_query_hash(self, query: str) -> str:
        """获取查询的哈希值"""
        return hashlib.md5(query.encode('utf-8')).hexdigest()
    
    def _calculate_similarity_score(self, query: str) -> float:
        """计算查询与相关领域的相似度分数"""
        if self.embedding_model is None or self.domain_embeddings is None:
            return 0.0
        
        try:
            query_embedding = self.embedding_model.encode([query])
            # 计算查询向量与所有领域向量的点积（即相似度分数）
            similarities = np.dot(self.domain_embeddings, query_embedding.T).flatten()
            # 取所有相似度分数中的最大值，作为最终的相似度分数
            max_similarity = np.max(similarities)
            return float(max_similarity)
        except Exception:
            return 0.0
    
    def generate_response(self, query: str, context: List[Dict], conversation_history: List[Dict] = None) -> str:
        """生成回答"""
        try:
            # 构建上下文
            context_text = self._build_context(context)
            history_text = self._build_history(conversation_history) if conversation_history else ""
            
            # 构建提示词
            prompt = self._build_prompt(query, context_text, history_text)
            
            # 调用API
            response = Generation.call(
                model=self.model,
                prompt=prompt,
                max_tokens=2048,  # 减少token数量，提高响应速度
                temperature=0.6,   # 降低温度，提高响应一致性
                top_p=0.9         # 提高top_p，增加响应多样性
            )
            
            if response.status_code == 200:
                return response.output.text
            else:
                return f"API调用失败: {response.message}"
                
        except Exception as e:
            return f"生成回答时出错: {str(e)}"
    
    def _build_context(self, context: List[Dict]) -> str:
        """构建上下文文本"""
        if not context:
            return ""
        
        context_text = "文档内容：\n"
        for i, (chunk, score) in enumerate(context, 1):
            context_text += f"{i}. {chunk['text']}\n"
        
        return context_text
    
    def _build_history(self, history: List[Dict]) -> str:
        """构建对话历史"""
        if not history:
            return ""
        
        history_text = "对话历史：\n"
        for msg in history[-3:]:  # 只保留最近3轮对话，减少token消耗
            role = "用户" if msg['role'] == 'user' else "助手"
            history_text += f"{role}: {msg['content']}\n"
        
        return history_text
    
    def _build_prompt(self, query: str, context: str, history: str) -> str:
        """构建完整提示词"""
        prompt = f"""{Config.SYSTEM_PROMPT}

{history}{context}

用户：{query}

回答："""
        
        return prompt
    
    def is_relevant_query(self, query: str) -> bool:
        """智能判断查询是否与线下店文档相关"""
        # 检查缓存
        query_hash = self._get_query_hash(query)
        if query_hash in self.relevance_cache:
            return self.relevance_cache[query_hash]
        
        # 简化的相关性判断
        relevance_score = self._calculate_simple_relevance(query)
        is_relevant = relevance_score >= 0.5  # 设置合理的阈值
        
        # 缓存结果
        self.relevance_cache[query_hash] = is_relevant
        self._save_relevance_cache()
        
        return is_relevant
    
    def _calculate_simple_relevance(self, query: str) -> float:
        """简化的相关性计算"""
        scores = []
        
        # 1. 关键词匹配判断
        keyword_score = self._calculate_keyword_score(query)
        scores.append(keyword_score)
        
        # 2. LLM语义判断
        llm_score = self._calculate_llm_relevance_score(query)
        scores.append(llm_score)
        
        # 加权平均 - 关键词匹配权重更高
        weights = [0.6, 0.4]  # 关键词、LLM判断的权重
        final_score = sum(score * weight for score, weight in zip(scores, weights))
        
        return final_score
    
    def _calculate_keyword_score(self, query: str) -> float:
        """计算关键词匹配分数"""
        relevant_keywords = [
            # 核心业务关键词
            '线下店', '教培', '教育', '培训', '机构', '选址', '装修', '运营',
            '财务', '成本', '现金流', '盈利', '风险', '投诉', '师资',
            '创业者', '负责人', '经理', '教练', '管家', '医生', 'Word',
            'word','Excel','excel','PPT','ppt','PPTX','pptx','PDF','pdf',
            '创业', '加盟', '直营', '联营', '加盟店', '直营店', '联营店', '加盟店管理',
            '推荐','辅导','方法','课程','教学','学员','招生','营销','推广',
            '服务','管理','团队','建设','文化','激励','沟通','协作',
            '风险','控制','合规','安全','质量','标准','流程','制度',
            '扩张','复制','连锁','品牌','统一','标准化','规模化',
            
            # 扩展业务关键词
            '店铺', '门店', '店面', '营业', '经营', '管理', '运营',
            '收入', '支出', '利润', '亏损', '预算', '投资', '回报',
            '人员', '员工', '招聘', '培训', '考核', '绩效', '薪资',
            '客户', '学员', '家长', '满意度', '投诉', '服务', '体验',
            '市场', '竞争', '定位', '策略', '计划', '目标', '指标',
            '设备', '设施', '环境', '装修', '设计', '布局', '空间',
            '课程', '教学', '教材', '教案', '评估', '测试', '成绩',
            '宣传', '广告', '推广', '营销', '销售', '转化', '成交',
            '法律', '合同', '协议', '条款', '责任', '义务', '权利',
            '数据', '分析', '统计', '报告', '监控', '预警', '改进'
        ]
        
        query_lower = query.lower()
        matched_keywords = sum(1 for keyword in relevant_keywords if keyword in query_lower)
        
        # 根据匹配关键词数量计算分数 - 更宽松的评分
        if matched_keywords == 0:
            return 0.0
        elif matched_keywords == 1:
            return 0.6  # 提高单关键词分数
        elif matched_keywords == 2:
            return 0.8  # 提高双关键词分数
        else:
            return 1.0  # 多关键词满分
    
    def _calculate_llm_relevance_score(self, query: str) -> float:
        """使用LLM计算相关性分数"""
        relevance_prompt = f"""请判断以下用户查询是否与线下店教培机构运营相关。

线下店教培机构相关主题包括：
- 选址评估与店铺规划
- 装修设计与空间布局
- 运营管理与日常运营
- 财务管理与成本控制
- 师资培训与团队建设
- 营销推广与招生策略
- 客户服务与满意度管理
- 课程设计与教学管理
- 风险控制与合规管理
- 多店复制与连锁扩张

用户查询：{query}

请只回答"相关"或"不相关"："""

        try:
            response = Generation.call(
                model=self.model,
                prompt=relevance_prompt,
                max_tokens=10,
                temperature=0.1,  # 低温度确保一致性
                top_p=0.9
            )
            
            if response.status_code == 200:
                result = response.output.text.strip().lower()
                return 1.0 if "相关" in result or "是" in result else 0.0
            else:
                return 0.0
                
        except Exception as e:
            return 0.0
    
    def _fallback_relevance_check(self, query: str) -> bool:
        """回退的相关性检查（关键词匹配）"""
        relevant_keywords = [
            '线下店', '教培', '教育', '培训', '机构', '选址', '装修', '运营',
            '财务', '成本', '现金流', '盈利', '风险', '投诉', '师资',
            '创业者', '负责人', '经理', '教练', '管家', '医生', 'Word',
            'word','Excel','excel','PPT','ppt','PPTX','pptx','PDF','pdf',
            '创业', '加盟', '直营', '联营', '加盟店', '直营店', '联营店', '加盟店管理',
            '推荐','辅导','方法','课程','教学','学员','招生','营销','推广',
            '服务','管理','团队','建设','文化','激励','沟通','协作',
            '风险','控制','合规','安全','质量','标准','流程','制度',
            '扩张','复制','连锁','品牌','统一','标准化','规模化',
            '线下店','教培','教育','培训','机构',
            '选址','装修','运营','财务','成本',
            '师资', '员工', '招聘', '培训', '考核',
            '学员', '家长', '满意度', '投诉', '服务',
            '营销', '推广', '宣传', '广告', '销售',
            '风险', '控制', '合规', '安全', '法律',
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in relevant_keywords)

if __name__ == "__main__":
    # 测试LLM客户端
    client = LLMClient()
    test_context = [({'text': '测试文档内容'}, 0.8)]
    response = client.generate_response("测试问题", test_context)
    print(f"测试响应: {response}")

