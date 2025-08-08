#!/usr/bin/env python3
"""
重新构建完整的向量知识库
"""

import os
import sys
from pdf_processor import PDFProcessor
from vector_store import VectorStore
from config import Config

def rebuild_knowledge_base():
    """重新构建知识库"""
    print("🔄 开始重新构建知识库...")
    print("=" * 50)
    
    # 1. 处理PDF文档
    print("📄 步骤1: 处理PDF文档")
    processor = PDFProcessor(Config.PDF_PATH)
    chunks = processor.process_document()
    
    if not chunks:
        print("❌ PDF处理失败，无法继续")
        return False
    
    print(f"✅ PDF处理完成，获得 {len(chunks)} 个文本块")
    
    # 2. 构建向量数据库
    print("\n🔍 步骤2: 构建向量数据库")
    vector_store = VectorStore()
    
    try:
        vector_store.add_chunks(chunks)
        print("✅ 向量化完成")
        
        # 3. 保存向量数据库
        print("\n💾 步骤3: 保存向量数据库")
        vector_store.save()
        
        # 4. 测试搜索功能
        print("\n🧪 步骤4: 测试搜索功能")
        test_queries = [
            "线下店选址",
            "成本控制",
            "现金流管理",
            "风险处理",
            "多店复制"
        ]
        
        for query in test_queries:
            results = vector_store.search(query, top_k=3)
            print(f"🔍 查询: '{query}' -> 找到 {len(results)} 个结果")
            if results:
                best_match = results[0]
                preview = best_match[0]['text'][:80] + "..." if len(best_match[0]['text']) > 80 else best_match[0]['text']
                print(f"   最佳匹配: {preview}")
        
        # 5. 显示统计信息
        print("\n📊 知识库统计信息:")
        print(f"  文档块数量: {len(vector_store.chunks)}")
        print(f"  向量数量: {len(vector_store.vectors)}")
        print(f"  向量维度: {len(vector_store.vectors[0]) if vector_store.vectors else 0}")
        
        # 计算平均块长度
        if vector_store.chunks:
            avg_length = sum(len(chunk['text']) for chunk in vector_store.chunks) / len(vector_store.chunks)
            print(f"  平均块长度: {avg_length:.1f} 字符")
        
        print("\n✅ 知识库重建完成！")
        return True
        
    except Exception as e:
        print(f"❌ 构建知识库失败: {e}")
        return False

def test_knowledge_base():
    """测试知识库功能"""
    print("\n🧪 测试知识库功能...")
    
    try:
        vector_store = VectorStore()
        
        # 测试加载
        if vector_store.load():
            print("✅ 知识库加载成功")
            
            # 测试搜索
            test_query = "线下店选址有什么注意事项"
            results = vector_store.search(test_query, top_k=5)
            
            print(f"🔍 测试查询: '{test_query}'")
            print(f"📊 搜索结果: {len(results)} 个")
            
            for i, (chunk, score) in enumerate(results[:3], 1):
                preview = chunk['text'][:100] + "..." if len(chunk['text']) > 100 else chunk['text']
                print(f"  {i}. 相似度 {score:.3f}: {preview}")
            
            return True
        else:
            print("❌ 知识库加载失败")
            return False
            
    except Exception as e:
        print(f"❌ 知识库测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🎯 重新构建教培管家知识库")
    print("=" * 50)
    
    # 重建知识库
    if rebuild_knowledge_base():
        print("\n" + "=" * 50)
        
        # 测试知识库
        if test_knowledge_base():
            print("\n🎉 知识库重建和测试全部成功！")
            print("💡 现在可以启动应用使用新的知识库了")
        else:
            print("\n⚠️ 知识库重建成功但测试失败")
    else:
        print("\n❌ 知识库重建失败")

if __name__ == "__main__":
    main()
