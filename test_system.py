#!/usr/bin/env python3
"""
系统测试脚本
"""

import os
import sys
from pathlib import Path

def test_pdf_processor():
    """测试PDF处理模块"""
    print("🔍 测试PDF处理模块...")
    try:
        from pdf_processor import PDFProcessor
        from config import Config
        
        processor = PDFProcessor(Config.PDF_PATH)
        chunks = processor.process_document()
        
        if chunks:
            print(f"✅ PDF处理成功，生成 {len(chunks)} 个文本块")
            return True
        else:
            print("❌ PDF处理失败")
            return False
    except Exception as e:
        print(f"❌ PDF处理模块测试失败: {e}")
        return False

def test_vector_store():
    """测试向量数据库模块"""
    print("🔍 测试向量数据库模块...")
    try:
        from vector_store import VectorStore
        
        store = VectorStore()
        
        # 测试数据
        test_chunks = [
            {'text': '线下店选址需要考虑人流量、交通便利性等因素', 'chunk_id': 0},
            {'text': '成本控制中租金不应超过总收入的15%', 'chunk_id': 1},
            {'text': '遇到学员投诉需要及时处理并建立信任', 'chunk_id': 2}
        ]
        
        store.add_chunks(test_chunks)
        
        # 测试搜索
        results = store.search("选址", top_k=2)
        
        if results:
            print(f"✅ 向量数据库测试成功，搜索到 {len(results)} 个结果")
            return True
        else:
            print("❌ 向量数据库搜索失败")
            return False
    except Exception as e:
        print(f"❌ 向量数据库模块测试失败: {e}")
        return False

def test_llm_client():
    """测试LLM客户端模块"""
    print("🔍 测试LLM客户端模块...")
    try:
        from llm_client import LLMClient
        
        client = LLMClient()
        
        # 测试相关性判断
        relevant_query = "线下店选址有什么注意事项？"
        irrelevant_query = "今天天气怎么样？"
        
        is_relevant = client.is_relevant_query(relevant_query)
        is_irrelevant = not client.is_relevant_query(irrelevant_query)
        
        if is_relevant and is_irrelevant:
            print("✅ LLM客户端相关性判断测试成功")
            return True
        else:
            print("❌ LLM客户端相关性判断测试失败")
            return False
    except Exception as e:
        print(f"❌ LLM客户端模块测试失败: {e}")
        return False

def test_agent():
    """测试智能Agent模块"""
    print("🔍 测试智能Agent模块...")
    try:
        from agent import IntelligentAgent
        
        # 创建Agent实例（不初始化知识库）
        agent = IntelligentAgent()
        
        # 测试快捷功能
        quick_actions = agent.get_quick_actions()
        if len(quick_actions) > 0:
            print(f"✅ 智能Agent测试成功，有 {len(quick_actions)} 个快捷功能")
            return True
        else:
            print("❌ 智能Agent快捷功能测试失败")
            return False
    except Exception as e:
        print(f"❌ 智能Agent模块测试失败: {e}")
        return False

def test_config():
    """测试配置模块"""
    print("🔍 测试配置模块...")
    try:
        from config import Config
        
        # 检查必要的配置项
        assert hasattr(Config, 'DASHSCOPE_API_KEY')
        assert hasattr(Config, 'PDF_PATH')
        assert hasattr(Config, 'CHUNK_SIZE')
        assert hasattr(Config, 'SYSTEM_PROMPT')
        
        print("✅ 配置模块测试成功")
        return True
    except Exception as e:
        print(f"❌ 配置模块测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 教培管家系统测试")
    print("=" * 50)
    
    tests = [
        test_config,
        test_pdf_processor,
        test_vector_store,
        test_llm_client,
        test_agent
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统可以正常运行。")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关模块。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

