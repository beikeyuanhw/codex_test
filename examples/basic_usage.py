"""基本使用示例

这个文件展示了如何使用LangGraph代理项目的基本功能。
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent import create_agent_graph, run_agent, arun_agent, Configuration

# 加载环境变量
load_dotenv()


def example_basic_usage():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 使用默认配置
    config = Configuration()
    
    # 简单查询
    query = "你好，请介绍一下你自己"
    print(f"查询: {query}")
    
    answer = run_agent(query, config)
    print(f"回答: {answer}")
    print()


def example_weather_tool():
    """天气工具使用示例"""
    print("=== 天气工具使用示例 ===")
    
    config = Configuration(
        enable_weather_tool=True,
        enable_search_tool=False,
        enable_calculator_tool=False
    )
    
    queries = [
        "北京今天天气怎么样？",
        "请告诉我上海的天气情况",
        "What's the weather like in Beijing?"
    ]
    
    for query in queries:
        print(f"查询: {query}")
        answer = run_agent(query, config)
        print(f"回答: {answer}")
        print()


def example_calculator_tool():
    """计算器工具使用示例"""
    print("=== 计算器工具使用示例 ===")
    
    config = Configuration(
        enable_weather_tool=False,
        enable_search_tool=False,
        enable_calculator_tool=True
    )
    
    queries = [
        "请计算 2 + 3 * 4",
        "sqrt(16) 等于多少？",
        "计算圆周率乘以2的结果"
    ]
    
    for query in queries:
        print(f"查询: {query}")
        answer = run_agent(query, config)
        print(f"回答: {answer}")
        print()


def example_search_tool():
    """搜索工具使用示例"""
    print("=== 搜索工具使用示例 ===")
    
    config = Configuration(
        enable_weather_tool=False,
        enable_search_tool=True,
        enable_calculator_tool=False
    )
    
    queries = [
        "搜索关于人工智能的信息",
        "查找Python编程相关内容",
        "搜索LangChain相关资料"
    ]
    
    for query in queries:
        print(f"查询: {query}")
        answer = run_agent(query, config)
        print(f"回答: {answer}")
        print()


def example_multi_tool():
    """多工具组合使用示例"""
    print("=== 多工具组合使用示例 ===")
    
    config = Configuration(
        enable_weather_tool=True,
        enable_search_tool=True,
        enable_calculator_tool=True
    )
    
    queries = [
        "请告诉我北京的天气，然后计算一下25摄氏度等于多少华氏度",
        "搜索一下人工智能的信息，然后计算2的10次方",
        "查询上海天气，搜索Python相关内容，最后计算圆的面积公式中半径为5时的面积"
    ]
    
    for query in queries:
        print(f"查询: {query}")
        answer = run_agent(query, config)
        print(f"回答: {answer}")
        print()


def example_custom_config():
    """自定义配置示例"""
    print("=== 自定义配置示例 ===")
    
    # 自定义配置
    config = Configuration(
        model_name="gpt-4o-mini",
        temperature=0.7,
        max_tokens=500,
        system_prompt="你是一个专业的技术顾问，专门帮助用户解决编程和技术问题。请用专业但易懂的语言回答问题。",
        enable_memory=True
    )
    
    # 使用相同的thread_id来测试记忆功能
    thread_id = "custom_session"
    
    queries = [
        "我想学习Python编程，应该从哪里开始？",
        "刚才你提到的内容中，哪个最重要？",  # 测试记忆功能
        "请推荐一些Python学习资源"
    ]
    
    for query in queries:
        print(f"查询: {query}")
        answer = run_agent(query, config, thread_id)
        print(f"回答: {answer}")
        print()


async def example_async_usage():
    """异步使用示例"""
    print("=== 异步使用示例 ===")
    
    config = Configuration()
    
    queries = [
        "请介绍一下LangGraph",
        "什么是人工智能代理？",
        "如何构建一个聊天机器人？"
    ]
    
    # 并发执行多个查询
    tasks = []
    for i, query in enumerate(queries):
        task = arun_agent(query, config, f"async_thread_{i}")
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    
    for query, answer in zip(queries, results):
        print(f"查询: {query}")
        print(f"回答: {answer}")
        print()


def example_graph_visualization():
    """图形可视化示例"""
    print("=== 图形结构示例 ===")
    
    config = Configuration()
    app = create_agent_graph(config)
    
    print("代理图形已创建")
    print(f"图形节点: {list(app.get_graph().nodes.keys())}")
    print(f"图形边: {list(app.get_graph().edges)}")
    print()
    
    # 如果安装了可视化依赖，可以生成图形
    try:
        # 注意：这需要安装额外的依赖包
        # pip install "langgraph[visualization]"
        graph_image = app.get_graph().draw_mermaid()
        print("Mermaid图形代码:")
        print(graph_image)
    except Exception as e:
        print(f"无法生成图形可视化: {e}")
        print("提示：安装可视化依赖 pip install 'langgraph[visualization]'")


def main():
    """主函数"""
    print("🤖 LangGraph代理项目使用示例\n")
    
    # 检查环境变量
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未设置OPENAI_API_KEY环境变量")
        print("请在.env文件中设置您的API密钥")
        print()
    
    try:
        # 运行各种示例
        example_basic_usage()
        example_weather_tool()
        example_calculator_tool()
        example_search_tool()
        example_multi_tool()
        example_custom_config()
        example_graph_visualization()
        
        # 运行异步示例
        print("运行异步示例...")
        asyncio.run(example_async_usage())
        
    except Exception as e:
        print(f"❌ 运行示例时出现错误: {e}")
        print("请检查您的配置和API密钥设置")


if __name__ == "__main__":
    main()