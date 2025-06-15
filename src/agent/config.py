"""配置管理模块

定义了LangGraph代理的可配置参数。
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class Configuration(BaseModel):
    """LangGraph代理的配置类
    
    这个类定义了代理运行时可以配置的参数，包括模型选择、
    系统提示词、工具启用状态等。
    """
    
    # 模型配置
    model_provider: str = Field(
        default="openai",
        description="LLM提供商 (openai, anthropic)"
    )
    model_name: str = Field(
        default="gpt-4o-mini",
        description="使用的模型名称"
    )
    temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="模型温度参数，控制输出的随机性"
    )
    max_tokens: Optional[int] = Field(
        default=1000,
        gt=0,
        description="最大输出token数"
    )
    
    # 系统配置
    system_prompt: str = Field(
        default="你是一个有用的AI助手，能够使用各种工具来帮助用户解决问题。请根据用户的需求选择合适的工具，并提供准确、有用的回答。",
        description="系统提示词"
    )
    
    # 工具配置
    enable_weather_tool: bool = Field(
        default=True,
        description="是否启用天气查询工具"
    )
    enable_search_tool: bool = Field(
        default=True,
        description="是否启用网络搜索工具"
    )
    enable_calculator_tool: bool = Field(
        default=True,
        description="是否启用计算器工具"
    )
    
    # 执行配置
    max_iterations: int = Field(
        default=10,
        gt=0,
        description="最大迭代次数"
    )
    enable_human_in_loop: bool = Field(
        default=False,
        description="是否启用人工干预"
    )
    
    # 内存配置
    enable_memory: bool = Field(
        default=True,
        description="是否启用对话记忆"
    )
    memory_key: str = Field(
        default="chat_history",
        description="内存存储的键名"
    )
    
    class Config:
        """Pydantic配置"""
        extra = "forbid"  # 禁止额外字段
        validate_assignment = True  # 启用赋值验证