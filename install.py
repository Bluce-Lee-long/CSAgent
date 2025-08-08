#!/usr/bin/env python3
"""
教培管家 - 自动安装脚本
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要Python 3.8或更高版本")
        return False
    print(f"✅ Python版本: {sys.version}")
    return True

def install_dependencies():
    """安装依赖包"""
    print("📦 安装依赖包...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ 依赖包安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False

def create_env_file():
    """创建环境变量文件"""
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env文件已存在")
        return True
    
    print("📝 创建.env文件...")
    try:
        with open(env_file, "w", encoding="utf-8") as f:
            f.write("# 阿里云通义千问API密钥\n")
            f.write("# 请在阿里云控制台获取API密钥并填入\n")
            f.write("DASHSCOPE_API_KEY=your_api_key_here\n")
        
        print("✅ .env文件创建成功")
        print("⚠️ 请编辑.env文件，填入您的API密钥")
        return True
    except Exception as e:
        print(f"❌ 创建.env文件失败: {e}")
        return False

def check_pdf_file():
    """检查PDF文件"""
    pdf_path = Path("线下店文档.pdf")
    if not pdf_path.exists():
        print("❌ 未找到PDF文件: 线下店文档.pdf")
        print("请确保PDF文件在项目根目录")
        return False
    
    print("✅ PDF文件已找到")
    return True

def run_tests():
    """运行系统测试"""
    print("🧪 运行系统测试...")
    try:
        result = subprocess.run([
            sys.executable, "test_system.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 系统测试通过")
            return True
        else:
            print("❌ 系统测试失败")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"❌ 运行测试失败: {e}")
        return False

def show_next_steps():
    """显示后续步骤"""
    print("\n" + "="*50)
    print("🎉 安装完成！")
    print("="*50)
    print("\n📋 后续步骤:")
    print("1. 编辑.env文件，填入您的阿里云API密钥")
    print("2. 运行: python run.py 启动应用")
    print("3. 在浏览器中访问显示的地址")
    print("\n💡 提示:")
    print("- 首次运行会处理PDF文档，请耐心等待")
    print("- 确保网络连接正常以访问API服务")
    print("- 如遇问题，请查看README.md文档")

def main():
    """主安装函数"""
    print("🎓 教培管家 - 智能客服Agent安装程序")
    print("="*50)
    
    # 检查Python版本
    if not check_python_version():
        return False
    
    # 检查PDF文件
    if not check_pdf_file():
        return False
    
    # 安装依赖
    if not install_dependencies():
        return False
    
    # 创建环境文件
    if not create_env_file():
        return False
    
    # 运行测试
    if not run_tests():
        print("⚠️ 测试失败，但安装已完成")
    
    # 显示后续步骤
    show_next_steps()
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

