"""多代理管理器测试"""

import os
import sys
from unittest.mock import patch, MagicMock

import pytest

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent import Configuration
from multiagent import MultiAgentManager


@patch('agent.graph.ChatOpenAI')
def test_relay_between_agents(mock_openai):
    """测试代理之间消息转发"""

    def make_llm(reply: str):
        mock_llm = MagicMock()
        mock_resp = MagicMock()
        mock_resp.content = reply
        mock_resp.tool_calls = []
        mock_llm.bind_tools.return_value.invoke.return_value = mock_resp
        return mock_llm

    mock_openai.side_effect = [make_llm("A1"), make_llm("B1")]

    configs = {
        "researcher": Configuration(enable_weather_tool=False, enable_search_tool=False, enable_calculator_tool=False),
        "critic": Configuration(enable_weather_tool=False, enable_search_tool=False, enable_calculator_tool=False),
    }

    manager = MultiAgentManager(configs)

    # 发送消息给researcher
    reply_a = manager.send_to_agent("researcher", "hello")
    assert reply_a == "A1"
    # researcher 回复 critic
    reply_b = manager.relay_message("researcher", "critic", reply_a)
    assert reply_b == "B1"

    # 检查历史记录
    assert any(msg.content == "A1" for msg in manager.histories["researcher"] if hasattr(msg, "content"))
    assert any(msg.content == "B1" for msg in manager.histories["critic"] if hasattr(msg, "content"))
