"""多代理交互示例

该脚本演示如何使用 ``MultiAgentManager`` 让两个代理互相交流。
"""

import os
import sys
from dotenv import load_dotenv

# 将 src 目录加入路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent import Configuration
from multiagent import MultiAgentManager

# 加载环境变量
load_dotenv()


def multiagent_demo():
    """运行两个代理相互对话的示例"""
    researcher_config = Configuration(
        enable_search_tool=True,
        enable_weather_tool=False,
        enable_calculator_tool=False,
        system_prompt="你是一名研究员，擅长查找资料并给出详细解答。",
    )

    critic_config = Configuration(
        enable_search_tool=False,
        enable_weather_tool=False,
        enable_calculator_tool=False,
        system_prompt="你是一名评论者，负责对研究员的回答提出批评和改进建议。",
    )

    manager = MultiAgentManager({"researcher": researcher_config, "critic": critic_config})

    question = "请简要介绍人工智能的前景。"
    print(f"用户: {question}")

    researcher_reply = manager.send_to_agent("researcher", question)
    print(f"研究员: {researcher_reply}")

    critic_reply = manager.relay_message("researcher", "critic", researcher_reply)
    print(f"评论员: {critic_reply}")


if __name__ == "__main__":
    multiagent_demo()
