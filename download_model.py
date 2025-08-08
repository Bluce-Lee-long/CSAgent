#!/usr/bin/env python3
"""
下载text2vec-base-chinese模型的脚本
支持多种下载方式和错误处理
"""

import os
import sys
import time
from pathlib import Path

def download_with_huggingface():
    """使用HuggingFace Hub下载模型"""
    try:
        from sentence_transformers import SentenceTransformer
        print("🔄 正在从HuggingFace下载text2vec-base-chinese模型...")
        
        # 设置下载参数
        model_name = "shibing624/text2vec-base-chinese"
        
        # 尝试下载模型
        model = SentenceTransformer(model_name, cache_folder="./models")
        
        print("✅ 模型下载成功！")
        print(f"📁 模型保存在: {os.path.abspath('./models')}")
        return True
        
    except Exception as e:
        print(f"❌ HuggingFace下载失败: {e}")
        return False

def download_with_git():
    """使用Git克隆模型仓库"""
    try:
        import subprocess
        print("🔄 正在使用Git克隆模型仓库...")
        
        # 创建models目录
        os.makedirs("./models", exist_ok=True)
        
        # 克隆仓库
        result = subprocess.run([
            "git", "clone", 
            "https://huggingface.co/shibing624/text2vec-base-chinese",
            "./models/text2vec-base-chinese"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Git克隆成功！")
            return True
        else:
            print(f"❌ Git克隆失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Git下载失败: {e}")
        return False

def download_with_curl():
    """使用curl下载模型文件"""
    try:
        import subprocess
        print("🔄 正在使用curl下载模型文件...")
        
        # 创建目录
        os.makedirs("./models/text2vec-base-chinese", exist_ok=True)
        
        # 需要下载的文件列表
        files = [
            "config.json",
            "pytorch_model.bin",
            "sentence_bert_config.json",
            "special_tokens_map.json",
            "tokenizer_config.json",
            "vocab.txt"
        ]
        
        base_url = "https://huggingface.co/shibing624/text2vec-base-chinese/resolve/main"
        
        for file in files:
            url = f"{base_url}/{file}"
            output_path = f"./models/text2vec-base-chinese/{file}"
            
            print(f"📥 下载 {file}...")
            result = subprocess.run([
                "curl", "-L", "-o", output_path, url
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ 下载 {file} 失败")
                return False
        
        print("✅ curl下载成功！")
        return True
        
    except Exception as e:
        print(f"❌ curl下载失败: {e}")
        return False

def test_model():
    """测试下载的模型"""
    try:
        from sentence_transformers import SentenceTransformer
        
        # 尝试加载本地模型 - 修复路径
        model_paths = [
            "./models/text2vec-base-chinese",
            "./models/shibing624_text2vec-base-chinese"
        ]
        
        for model_path in model_paths:
            if os.path.exists(model_path):
                print(f"🧪 测试本地模型: {model_path}")
                model = SentenceTransformer(model_path)
                
                # 测试编码
                texts = ["这是一个测试句子", "线下店选址需要考虑人流量"]
                embeddings = model.encode(texts)
                
                print(f"✅ 模型测试成功！编码了 {len(texts)} 个句子")
                return True
        
        print("❌ 本地模型文件不存在")
        return False
        
    except Exception as e:
        print(f"❌ 模型测试失败: {e}")
        return False

def create_offline_model():
    """创建离线模型配置"""
    try:
        config = {
            "model_name": "shibing624/text2vec-base-chinese",
            "local_path": "./models/text2vec-base-chinese",
            "cache_dir": "./models"
        }
        
        import json
        with open("./models/model_config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print("✅ 离线模型配置已创建")
        return True
        
    except Exception as e:
        print(f"❌ 创建配置失败: {e}")
        return False

def main():
    """主下载函数"""
    print("🎯 text2vec-base-chinese 模型下载工具")
    print("=" * 50)
    
    # 检查是否已存在
    if os.path.exists("./models/text2vec-base-chinese"):
        print("✅ 模型已存在，跳过下载")
        if test_model():
            return True
    
    # 尝试不同的下载方式
    methods = [
        ("HuggingFace Hub", download_with_huggingface),
        ("Git克隆", download_with_git),
        ("curl下载", download_with_curl)
    ]
    
    for method_name, method_func in methods:
        print(f"\n🔄 尝试使用 {method_name} 下载...")
        if method_func():
            print(f"✅ {method_name} 下载成功！")
            
            # 测试模型
            if test_model():
                create_offline_model()
                return True
            else:
                print("⚠️ 模型下载成功但测试失败")
        
        print(f"❌ {method_name} 下载失败，尝试下一种方式...")
        time.sleep(2)
    
    print("\n❌ 所有下载方式都失败了")
    print("💡 建议：")
    print("1. 检查网络连接")
    print("2. 使用代理")
    print("3. 手动下载模型文件")
    print("4. 使用离线模式")
    
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
