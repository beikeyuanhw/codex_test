"""Simplified configuration module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Configuration:
    """Configuration options for the agent."""

    # Model options
    model_provider: str = "openai"
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.1
    max_tokens: Optional[int] = 1000

    # System behaviour
    system_prompt: str = (
        "你是一个有用的AI助手，能够使用各种工具来帮助用户解决问题。请根据用户的需求选择合适的工具，并提供准确、有用的回答。"
    )

    # Tool toggles
    enable_weather_tool: bool = True
    enable_search_tool: bool = True
    enable_calculator_tool: bool = True

    # Execution options
    max_iterations: int = 10
    enable_human_in_loop: bool = False

    # Memory
    enable_memory: bool = True
    memory_key: str = "chat_history"

    def __post_init__(self) -> None:
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")
        if self.max_tokens is not None and self.max_tokens <= 0:
            raise ValueError("max_tokens must be greater than 0")
        if self.max_iterations <= 0:
            raise ValueError("max_iterations must be greater than 0")
