"""深度研究示例

该脚本演示如何使用 LangGraph 代理进行较为复杂的研究会话。
脚本会在同一线程中连续提出多个问题，展示记忆和多工具组合的效果。
"""

import os
import sys
from dotenv import load_dotenv

# 将 src 目录加入路径，便于直接导入包
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent import Configuration, run_agent

# 加载环境变量（如 OPENAI_API_KEY）
load_dotenv()


def deep_research_demo():
    """运行深度研究示例"""
    print("=== 深度研究 Demo ===")

    # 自定义配置：启用搜索与计算器工具，开启记忆
    config = Configuration(
        enable_weather_tool=False,
        enable_search_tool=True,
        enable_calculator_tool=True,
        system_prompt=(
            "你是一位学术研究助手，善于搜索资料并汇总关键信息，"
            "在必要时还能进行数学计算帮助分析。"
        ),
    )

    thread_id = "deep_research_session"
    queries = [
        "请简要介绍人工智能的发展历史。",
        "列出人工智能领域的三个重要里程碑。",
        "计算一下 2024 减去 1956 等于多少。",
    ]

    for query in queries:
        print(f"\n用户: {query}")
        answer = run_agent(query, config, thread_id)
        print(f"代理: {answer}")


if __name__ == "__main__":
    deep_research_demo()
