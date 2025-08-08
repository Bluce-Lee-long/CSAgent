import json
import os
import hashlib
from typing import Dict, Optional
from datetime import datetime

class QuickActionCache:
    """快捷功能缓存管理器"""
    
    def __init__(self, cache_file: str = "quick_action_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """加载缓存文件"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载缓存文件失败: {e}")
                return {}
        return {}
    
    def _save_cache(self):
        """保存缓存到文件"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存缓存文件失败: {e}")
    
    def _generate_cache_key(self, query: str) -> str:
        """生成缓存键"""
        # 使用查询内容的哈希作为缓存键
        return hashlib.md5(query.encode('utf-8')).hexdigest()
    
    def get_cached_response(self, query: str) -> Optional[str]:
        """获取缓存的响应"""
        cache_key = self._generate_cache_key(query)
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            # 检查缓存是否过期（可选，这里设置30天过期）
            if 'timestamp' in cached_data:
                cache_time = datetime.fromisoformat(cached_data['timestamp'])
                if (datetime.now() - cache_time).days < 30:
                    return cached_data['response']
            else:
                return cached_data['response']
        return None
    
    def cache_response(self, query: str, response: str):
        """缓存响应结果"""
        cache_key = self._generate_cache_key(query)
        self.cache[cache_key] = {
            'query': query,
            'response': response,
            'timestamp': datetime.now().isoformat()
        }
        self._save_cache()
    
    def clear_cache(self):
        """清空缓存"""
        self.cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
    
    def get_cache_stats(self) -> Dict:
        """获取缓存统计信息"""
        return {
            'total_cached': len(self.cache),
            'cache_file': self.cache_file,
            'cache_size': os.path.getsize(self.cache_file) if os.path.exists(self.cache_file) else 0
        }
