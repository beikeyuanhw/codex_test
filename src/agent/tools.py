"""工具定义模块

定义了代理可以使用的各种工具函数。
"""

from typing import Dict, Any

try:  # 如果缺少 langchain_core, 提供简易 tool 装饰器
    from langchain_core.tools import tool
except Exception:  # pragma: no cover - fallback for limited env
    def tool(func):
        """Fallback tool decorator doing nothing."""
        return func


@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息
    
    Args:
        city: 城市名称，例如 "北京" 或 "Beijing"
        
    Returns:
        包含天气信息的字符串
    """
    # 这里是一个模拟的天气API调用
    # 在实际应用中，你应该调用真实的天气API
    weather_data = {
        "北京": "晴天，温度 15-25°C，微风",
        "上海": "多云，温度 18-28°C，东南风",
        "广州": "小雨，温度 20-30°C，南风",
        "深圳": "晴天，温度 22-32°C，微风",
        "Beijing": "Sunny, 15-25°C, light breeze",
        "Shanghai": "Cloudy, 18-28°C, southeast wind",
        "Guangzhou": "Light rain, 20-30°C, south wind",
        "Shenzhen": "Sunny, 22-32°C, light breeze",
    }
    
    return weather_data.get(city, f"抱歉，暂时无法获取{city}的天气信息。请检查城市名称是否正确。")


@tool
def search_web(query: str, num_results: int = 3) -> str:
    """在网络上搜索信息
    
    Args:
        query: 搜索查询词
        num_results: 返回结果数量，默认为3
        
    Returns:
        搜索结果的摘要字符串
    """
    # 这里是一个模拟的搜索功能
    # 在实际应用中，你应该集成真实的搜索API（如Google Search API、Bing Search API等）
    
    mock_results = {
        "人工智能": [
            "人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
            "机器学习是人工智能的一个子集，通过算法让计算机从数据中学习模式。",
            "深度学习使用神经网络来模拟人脑的工作方式，在图像识别和自然语言处理方面取得了重大突破。"
        ],
        "Python编程": [
            "Python是一种高级编程语言，以其简洁的语法和强大的功能而闻名。",
            "Python广泛应用于数据科学、机器学习、Web开发和自动化脚本等领域。",
            "Python拥有丰富的第三方库生态系统，如NumPy、Pandas、Django等。"
        ],
        "LangChain": [
            "LangChain是一个用于构建基于大型语言模型应用程序的框架。",
            "LangGraph是LangChain生态系统的一部分，专门用于构建有状态的代理工作流。",
            "LangChain提供了丰富的工具和组件，简化了LLM应用的开发过程。"
        ]
    }
    
    # 简单的关键词匹配
    results = []
    for key, values in mock_results.items():
        if key in query or any(word in query for word in key.split()):
            results.extend(values[:num_results])
            break
    
    if not results:
        results = [f"关于'{query}'的搜索结果：这是一个模拟搜索结果。在实际应用中，这里会显示真实的网络搜索结果。"]
    
    return "\n\n".join(f"{i+1}. {result}" for i, result in enumerate(results[:num_results]))


@tool
def calculate(expression: str) -> str:
    """执行数学计算
    
    Args:
        expression: 数学表达式，例如 "2 + 3 * 4" 或 "sqrt(16)"
        
    Returns:
        计算结果的字符串
    """
    try:
        # 为了安全起见，只允许基本的数学运算
        import math
        
        # 定义允许的函数和常量
        allowed_names = {
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "pow": pow,
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log,
            "log10": math.log10,
            "exp": math.exp,
            "pi": math.pi,
            "e": math.e,
        }
        
        # 安全地评估表达式
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"计算结果：{expression} = {result}"
        
    except Exception as e:
        return f"计算错误：{str(e)}。请检查表达式是否正确。"


# 工具列表，用于在图中注册
AVAILABLE_TOOLS = {
    "weather": get_weather,
    "search": search_web,
    "calculator": calculate,
}


def get_enabled_tools(config) -> list:
    """根据配置获取启用的工具列表
    
    Args:
        config: Configuration对象
        
    Returns:
        启用的工具列表
    """
    tools = []
    
    if config.enable_weather_tool:
        tools.append(get_weather)
    
    if config.enable_search_tool:
        tools.append(search_web)
        
    if config.enable_calculator_tool:
        tools.append(calculate)
    
    return tools
