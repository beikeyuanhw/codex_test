#!/usr/bin/env python3
"""快速启动脚本

这个脚本提供了一个简单的方式来启动LangGraph代理项目。
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """检查依赖是否已安装"""
    try:
        import langgraph
        import langchain
        import fastapi
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -e .")
        return False

def check_env_file():
    """检查环境变量文件"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  未找到.env文件")
        print("请复制.env.example到.env并配置您的API密钥")
        return False
    return True

def main():
    """主函数"""
    print("🤖 LangGraph Agent Project 启动器")
    print("=" * 40)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查环境文件
    if not check_env_file():
        print("\n继续运行可能会遇到API密钥错误...")
    
    print("\n请选择运行模式:")
    print("1. 交互模式 (推荐新手)")
    print("2. Web API服务")
    print("3. LangGraph Studio (推荐开发者)")
    print("4. 运行示例")
    print("5. 运行测试")
    print("0. 退出")
    
    while True:
        try:
            choice = input("\n请输入选择 (0-5): ").strip()
            
            if choice == "0":
                print("👋 再见！")
                break
            elif choice == "1":
                print("\n🚀 启动交互模式...")
                subprocess.run([sys.executable, "src/main.py", "--mode", "interactive"])
            elif choice == "2":
                print("\n🚀 启动Web API服务...")
                print("访问 http://localhost:8000/docs 查看API文档")
                subprocess.run([sys.executable, "src/main.py", "--mode", "server"])
            elif choice == "3":
                print("\n🚀 启动LangGraph Studio...")
                try:
                    subprocess.run(["langgraph", "dev"])
                except FileNotFoundError:
                    print("❌ 未找到langgraph命令")
                    print("请安装: pip install 'langgraph-cli[inmem]'")
            elif choice == "4":
                print("\n🚀 运行示例...")
                subprocess.run([sys.executable, "examples/basic_usage.py"])
            elif choice == "5":
                print("\n🚀 运行测试...")
                try:
                    subprocess.run(["pytest", "tests/", "-v"])
                except FileNotFoundError:
                    print("❌ 未找到pytest命令")
                    print("请安装: pip install pytest pytest-asyncio")
            else:
                print("❌ 无效选择，请输入0-5之间的数字")
                
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 运行时错误: {e}")

if __name__ == "__main__":
    main()