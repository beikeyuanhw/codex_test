"""代理功能测试

这个文件包含了对LangGraph代理项目的单元测试。
"""

import os
import sys
import pytest
import asyncio
from unittest.mock import patch, MagicMock

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent import Configuration, create_agent_graph, run_agent, arun_agent
from agent.tools import get_weather, search_web, calculate, get_enabled_tools


class TestConfiguration:
    """配置类测试"""
    
    def test_default_configuration(self):
        """测试默认配置"""
        config = Configuration()
        
        assert config.model_provider == "openai"
        assert config.model_name == "gpt-4o-mini"
        assert config.temperature == 0.1
        assert config.enable_weather_tool is True
        assert config.enable_search_tool is True
        assert config.enable_calculator_tool is True
        assert config.enable_memory is True
    
    def test_custom_configuration(self):
        """测试自定义配置"""
        config = Configuration(
            model_provider="anthropic",
            model_name="claude-3-sonnet",
            temperature=0.5,
            enable_weather_tool=False
        )
        
        assert config.model_provider == "anthropic"
        assert config.model_name == "claude-3-sonnet"
        assert config.temperature == 0.5
        assert config.enable_weather_tool is False
    
    def test_configuration_validation(self):
        """测试配置验证"""
        # 测试温度范围验证
        with pytest.raises(ValueError):
            Configuration(temperature=-1.0)
        
        with pytest.raises(ValueError):
            Configuration(temperature=3.0)
        
        # 测试正常范围
        config = Configuration(temperature=1.0)
        assert config.temperature == 1.0


class TestTools:
    """工具功能测试"""
    
    def test_get_weather_tool(self):
        """测试天气工具"""
        # 测试已知城市
        result = get_weather("北京")
        assert "北京" in result or "晴天" in result
        
        result = get_weather("Beijing")
        assert "Beijing" in result or "Sunny" in result
        
        # 测试未知城市
        result = get_weather("UnknownCity")
        assert "抱歉" in result or "无法获取" in result
    
    def test_search_web_tool(self):
        """测试网络搜索工具"""
        # 测试已知关键词
        result = search_web("人工智能")
        assert "人工智能" in result or "AI" in result
        
        result = search_web("Python编程")
        assert "Python" in result
        
        # 测试结果数量限制
        result = search_web("test", num_results=1)
        assert len(result.split("\n\n")) <= 1
    
    def test_calculate_tool(self):
        """测试计算器工具"""
        # 测试基本运算
        result = calculate("2 + 3")
        assert "5" in result
        
        result = calculate("2 * 3")
        assert "6" in result
        
        # 测试数学函数
        result = calculate("sqrt(16)")
        assert "4" in result
        
        # 测试错误表达式
        result = calculate("invalid_expression")
        assert "错误" in result or "Error" in result
    
    def test_get_enabled_tools(self):
        """测试获取启用工具"""
        # 测试全部启用
        config = Configuration(
            enable_weather_tool=True,
            enable_search_tool=True,
            enable_calculator_tool=True
        )
        tools = get_enabled_tools(config)
        assert len(tools) == 3
        
        # 测试部分启用
        config = Configuration(
            enable_weather_tool=True,
            enable_search_tool=False,
            enable_calculator_tool=False
        )
        tools = get_enabled_tools(config)
        assert len(tools) == 1
        
        # 测试全部禁用
        config = Configuration(
            enable_weather_tool=False,
            enable_search_tool=False,
            enable_calculator_tool=False
        )
        tools = get_enabled_tools(config)
        assert len(tools) == 0


class TestAgentGraph:
    """代理图形测试"""
    
    def test_create_agent_graph(self):
        """测试创建代理图形"""
        config = Configuration()
        app = create_agent_graph(config)
        
        assert app is not None
        
        # 检查图形结构
        graph = app.get_graph()
        assert "agent" in graph.nodes
        
        # 如果启用了工具，应该有tools节点
        if any([config.enable_weather_tool, config.enable_search_tool, config.enable_calculator_tool]):
            assert "tools" in graph.nodes
    
    def test_create_agent_graph_no_tools(self):
        """测试创建无工具的代理图形"""
        config = Configuration(
            enable_weather_tool=False,
            enable_search_tool=False,
            enable_calculator_tool=False
        )
        app = create_agent_graph(config)
        
        assert app is not None
        
        # 检查图形结构
        graph = app.get_graph()
        assert "agent" in graph.nodes
        assert "tools" not in graph.nodes


class TestAgentExecution:
    """代理执行测试"""
    
    @patch('agent.graph.ChatOpenAI')
    def test_run_agent_mock(self, mock_openai):
        """使用模拟LLM测试代理运行"""
        # 模拟LLM响应
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "这是一个测试响应"
        mock_response.tool_calls = []
        mock_llm.bind_tools.return_value.invoke.return_value = mock_response
        mock_openai.return_value = mock_llm
        
        config = Configuration()
        result = run_agent("测试查询", config)
        
        assert "测试响应" in result
    
    @pytest.mark.asyncio
    @patch('agent.graph.ChatOpenAI')
    async def test_arun_agent_mock(self, mock_openai):
        """使用模拟LLM测试异步代理运行"""
        # 模拟LLM响应
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "这是一个异步测试响应"
        mock_response.tool_calls = []
        
        # 模拟异步调用
        async def mock_ainvoke(*args, **kwargs):
            return {"messages": [mock_response]}
        
        mock_app = MagicMock()
        mock_app.ainvoke = mock_ainvoke
        
        with patch('agent.graph.create_agent_graph', return_value=mock_app):
            config = Configuration()
            result = await arun_agent("异步测试查询", config)
            
            assert "异步测试响应" in result


class TestIntegration:
    """集成测试"""
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="需要OPENAI_API_KEY环境变量"
    )
    def test_real_agent_execution(self):
        """真实代理执行测试（需要API密钥）"""
        config = Configuration(
            enable_weather_tool=True,
            enable_search_tool=False,
            enable_calculator_tool=False,
            max_tokens=100
        )
        
        result = run_agent("你好", config)
        assert isinstance(result, str)
        assert len(result) > 0
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="需要OPENAI_API_KEY环境变量"
    )
    def test_tool_usage(self):
        """工具使用测试（需要API密钥）"""
        config = Configuration(
            enable_weather_tool=True,
            enable_search_tool=False,
            enable_calculator_tool=True,
            max_tokens=200
        )
        
        # 测试天气工具
        result = run_agent("北京天气怎么样？", config)
        assert isinstance(result, str)
        
        # 测试计算器工具
        result = run_agent("计算2+2等于多少", config)
        assert isinstance(result, str)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])