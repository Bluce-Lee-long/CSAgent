import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
from config import Config

class VectorStore:
    def __init__(self, model_name: str = "./models/shibing624_text2vec-base-chinese"):
        # 优先使用本地模型，如果不存在则使用在线模型
        if os.path.exists(model_name):
            self.model = SentenceTransformer(model_name)
            print(f"✅ 使用本地模型: {model_name}")
        else:
            print("⚠️ 本地模型不存在，尝试使用在线模型...")
            self.model = SentenceTransformer("shibing624/text2vec-base-chinese")
        
        self.vectors = []
        self.chunks = []
        self.db_path = Config.VECTOR_DB_PATH
        
        # 创建向量数据库目录
        os.makedirs(self.db_path, exist_ok=True)
    
    def add_chunks(self, chunks: List[Dict]):
        """添加文档块到向量数据库"""
        print("正在生成文本向量...")
        
        texts = [chunk['text'] for chunk in chunks]
        vectors = self.model.encode(texts, show_progress_bar=True)
        
        self.vectors = vectors.tolist()
        self.chunks = chunks
        
        print(f"向量化完成，共 {len(self.vectors)} 个向量")
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """搜索最相关的文档块"""
        # 编码查询
        query_vector = self.model.encode([query])
        
        # 计算相似度
        similarities = []
        for vector in self.vectors:
            similarity = np.dot(query_vector[0], vector) / (
                np.linalg.norm(query_vector[0]) * np.linalg.norm(vector)
            )
            similarities.append(similarity)
        
        # 获取top_k结果
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append((self.chunks[idx], similarities[idx]))
        
        return results
    
    def save(self):
        """保存向量数据库"""
        data = {
            'vectors': self.vectors,
            'chunks': self.chunks
        }
        
        with open(os.path.join(self.db_path, 'vector_db.pkl'), 'wb') as f:
            pickle.dump(data, f)
        
        print(f"向量数据库已保存到 {self.db_path}")
    
    def load(self):
        """加载向量数据库"""
        db_file = os.path.join(self.db_path, 'vector_db.pkl')
        
        if os.path.exists(db_file):
            with open(db_file, 'rb') as f:
                data = pickle.load(f)
            
            self.vectors = data['vectors']
            self.chunks = data['chunks']
            print(f"向量数据库已加载，共 {len(self.vectors)} 个向量")
            return True
        else:
            print("向量数据库文件不存在")
            return False

if __name__ == "__main__":
    # 测试向量数据库
    store = VectorStore()
    test_chunks = [
        {'text': '线下店选址需要考虑人流量、交通便利性等因素', 'chunk_id': 0},
        {'text': '成本控制中租金不应超过总收入的15%', 'chunk_id': 1},
        {'text': '遇到学员投诉需要及时处理并建立信任', 'chunk_id': 2}
    ]
    store.add_chunks(test_chunks)
    store.save()
    
    # 测试搜索
    results = store.search("选址", top_k=2)
    print(f"搜索结果: {len(results)} 个")
    for chunk, score in results:
        print(f"相似度 {score:.3f}: {chunk['text'][:50]}...")

