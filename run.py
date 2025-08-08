#!/usr/bin/env python3
"""
教培管家 - 智能客服Agent启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import streamlit
        import dashscope
        import sentence_transformers
        import PyPDF2
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_api_key():
    """检查API密钥是否配置"""
    from config import Config
    if not Config.DASHSCOPE_API_KEY:
        print("❌ 未配置API密钥")
        print("请设置环境变量 DASHSCOPE_API_KEY")
        print("或创建 .env 文件并填入密钥")
        return False
    else:
        print("✅ API密钥已配置")
        return True

def check_pdf_file():
    """检查PDF文件是否存在"""
    pdf_path = Path("线下店文档.pdf")
    if not pdf_path.exists():
        print("❌ 未找到PDF文件: 线下店文档.pdf")
        return False
    else:
        print("✅ PDF文件已找到")
        return True

def main():
    """主函数"""
    print("🎓 教培管家 - 智能客服Agent")
    print("=" * 50)
    
    # 检查环境
    if not check_dependencies():
        return
    
    if not check_api_key():
        return
    
    if not check_pdf_file():
        return
    
    print("\n🚀 启动Web界面...")
    print("请在浏览器中访问显示的地址")
    print("按 Ctrl+C 停止服务")
    print("-" * 50)
    
    # 启动Streamlit应用
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 服务已停止")

if __name__ == "__main__":
    main()

