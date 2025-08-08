#!/usr/bin/env python3
"""
分析PDF文档结构，为分块配置提供依据
"""

import PyPDF2
import re
from collections import Counter

def analyze_pdf_structure():
    """分析PDF文档结构"""
    pdf_path = "线下店文档.pdf"
    
    print("📊 PDF文档结构分析")
    print("=" * 50)
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            print(f"📄 文档基本信息:")
            print(f"  总页数: {len(pdf_reader.pages)} 页")
            
            # 分析每页内容
            page_stats = []
            all_text = ""
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                if text.strip():
                    page_length = len(text)
                    page_stats.append({
                        'page': page_num,
                        'length': page_length,
                        'text': text
                    })
                    all_text += text + "\n"
                    
                    print(f"  第{page_num}页: {page_length} 字符")
            
            print(f"\n📊 统计信息:")
            print(f"  总字符数: {len(all_text)}")
            print(f"  平均页长度: {len(all_text) // len(page_stats)} 字符")
            print(f"  最长页: {max(p['length'] for p in page_stats)} 字符")
            print(f"  最短页: {min(p['length'] for p in page_stats)} 字符")
            
            # 分析内容结构
            analyze_content_structure(all_text)
            
            return page_stats, all_text
            
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return None, None

def analyze_content_structure(text):
    """分析内容结构"""
    print(f"\n🔍 内容结构分析:")
    
    # 查找章节标题
    chapter_patterns = [
        r'第[一二三四五六七八九十\d]+[章节]',
        r'[一二三四五六七八九十\d]+[、.][^。\n]+',
        r'[A-Z][A-Z\s]+',
        r'[一二三四五六七八九十\d]+[.、]\s*[^。\n]+'
    ]
    
    chapters = []
    for pattern in chapter_patterns:
        matches = re.findall(pattern, text)
        chapters.extend(matches)
    
    print(f"  发现章节标记: {len(chapters)} 个")
    if chapters:
        print("  主要章节:")
        for i, chapter in enumerate(chapters[:10], 1):
            print(f"    {i}. {chapter}")
    
    # 分析关键词
    keywords = [
        '选址', '成本', '现金流', '风险', '运营', '管理', '财务', '盈利',
        '装修', '人员', '培训', '营销', '客户', '服务', '质量', '标准'
    ]
    
    print(f"\n📈 关键词频率:")
    for keyword in keywords:
        count = text.count(keyword)
        if count > 0:
            print(f"  {keyword}: {count} 次")
    
    # 分析句子长度
    sentences = re.split(r'[。！？]', text)
    sentence_lengths = [len(s.strip()) for s in sentences if s.strip()]
    
    if sentence_lengths:
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths)
        print(f"\n📏 句子长度分析:")
        print(f"  平均句子长度: {avg_sentence_length:.1f} 字符")
        print(f"  最长句子: {max(sentence_lengths)} 字符")
        print(f"  最短句子: {min(sentence_lengths)} 字符")

def suggest_chunk_config():
    """建议分块配置"""
    print(f"\n🎯 分块配置建议:")
    print("=" * 50)
    
    # 基于分析结果建议配置
    print("基于文档特点，建议以下配置:")
    print()
    print("1. 小分块配置 (适合精确检索):")
    print("   CHUNK_SIZE = 400-600")
    print("   CHUNK_OVERLAP = 50-100")
    print("   优点: 检索精度高，适合具体问题")
    print("   缺点: 上下文可能不完整")
    print()
    print("2. 中等分块配置 (平衡配置):")
    print("   CHUNK_SIZE = 600-800")
    print("   CHUNK_OVERLAP = 100-150")
    print("   优点: 平衡精度和上下文")
    print("   缺点: 需要更多存储空间")
    print()
    print("3. 大分块配置 (适合复杂问题):")
    print("   CHUNK_SIZE = 800-1200")
    print("   CHUNK_OVERLAP = 150-200")
    print("   优点: 上下文完整，适合综合分析")
    print("   缺点: 检索精度可能降低")
    print()
    print("💡 推荐配置:")
    print("   考虑到教培文档的专业性和完整性，建议使用中等分块配置")
    print("   CHUNK_SIZE = 700")
    print("   CHUNK_OVERLAP = 120")

def main():
    """主函数"""
    print("🔍 PDF文档分析工具")
    print("=" * 50)
    
    # 分析PDF结构
    page_stats, all_text = analyze_pdf_structure()
    
    if page_stats and all_text:
        # 建议配置
        suggest_chunk_config()
        
        print(f"\n📋 当前配置:")
        print(f"  CHUNK_SIZE = 800")
        print(f"  CHUNK_OVERLAP = 100")
        print()
        print("🔄 是否要更新配置？")

if __name__ == "__main__":
    main()
