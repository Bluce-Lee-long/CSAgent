#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from llm_client import LLMClient

def debug_keywords():
    client = LLMClient()
    
    test_queries = [
        "线下店选址有什么注意事项？",
        "线下店的装修设计要点是什么？",
        "如何控制教培机构的运营成本？"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        keyword_score = client._calculate_keyword_score(query)
        llm_score = client._calculate_llm_relevance_score(query)
        final_score = client._calculate_simple_relevance(query)
        
        print(f"关键词分数: {keyword_score:.3f}")
        print(f"LLM分数: {llm_score:.3f}")
        print(f"最终分数: {final_score:.3f}")
        print(f"判定结果: {'相关' if final_score >= 0.5 else '不相关'}")

if __name__ == "__main__":
    debug_keywords()
