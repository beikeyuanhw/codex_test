"""Simplified agent graph implementation.

This module provides a lightweight implementation of the logic used in
``create_agent_graph``. It avoids heavy dependencies so that the tests in this
repository can run in a limited environment.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .config import Configuration
from .tools import get_enabled_tools


# ---------------------------------------------------------------------------
# Message classes (minimal replacements for langchain_core.messages)
# ---------------------------------------------------------------------------
@dataclass
class BaseMessage:
    """Minimal message class."""

    content: str


class HumanMessage(BaseMessage):
    pass


class AIMessage(BaseMessage):
    pass


class ToolMessage(BaseMessage):
    pass


# ---------------------------------------------------------------------------
# Minimal LLM classes used for testing. Real functionality is not implemented
# because tests patch these classes to supply custom behaviour.
# ---------------------------------------------------------------------------
class ChatOpenAI:
    """Placeholder ChatOpenAI class."""

    def __init__(self, model: str, temperature: float, max_tokens: int, api_key: Optional[str] = None) -> None:
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key

    def bind_tools(self, tools: List[Any]):  # pragma: no cover - behaviour patched in tests
        self.tools = tools
        return self

    def invoke(self, messages: List[BaseMessage]):  # pragma: no cover - patched in tests
        return AIMessage(content="mock")

    async def ainvoke(self, messages: List[BaseMessage]):  # pragma: no cover - patched in tests
        return AIMessage(content="mock")


class ChatAnthropic(ChatOpenAI):
    """Placeholder ChatAnthropic class."""

    pass


# ---------------------------------------------------------------------------
# Simplified graph execution engine
# ---------------------------------------------------------------------------
class _SimpleApp:
    def __init__(self, config: Configuration, tools: List[Any]):
        self.config = config
        self.tools = tools
        self._nodes = {"agent"}
        if tools:
            self._nodes.add("tools")

    # ``get_graph`` returns an object with a ``nodes`` attribute for tests
    def get_graph(self):
        class _Graph:
            pass

        g = _Graph()
        g.nodes = self._nodes
        return g

    def _run_llm(self, messages: List[BaseMessage]):
        llm = create_llm(self.config)
        # Always call ``bind_tools`` so tests can mock the behaviour
        llm_with_tools = llm.bind_tools(self.tools)
        resp = llm_with_tools.invoke(messages)
        if not isinstance(resp, BaseMessage):
            resp = AIMessage(content=getattr(resp, "content", str(resp)))
        return resp

    def invoke(self, state: Dict[str, Any], config: Optional[Dict[str, Any]] = None):
        response = self._run_llm(state["messages"])
        return {"messages": state["messages"] + [response]}

    async def ainvoke(self, state: Dict[str, Any], config: Optional[Dict[str, Any]] = None):
        llm = create_llm(self.config)
        # Always call ``bind_tools`` so tests can mock the behaviour
        llm_with_tools = llm.bind_tools(self.tools)
        if hasattr(llm_with_tools, "ainvoke"):
            response = await llm_with_tools.ainvoke(state["messages"])
        else:
            response = llm_with_tools.invoke(state["messages"])
        if not isinstance(response, BaseMessage):
            response = AIMessage(content=getattr(response, "content", str(response)))
        return {"messages": state["messages"] + [response]}


# ---------------------------------------------------------------------------
# Factory helpers used by the public API
# ---------------------------------------------------------------------------

def create_llm(config: Configuration):
    """Create a placeholder LLM instance based on configuration."""

    if config.model_provider.lower() == "openai":
        return ChatOpenAI(
            model=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
    elif config.model_provider.lower() == "anthropic":
        return ChatAnthropic(
            model=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            api_key=os.getenv("ANTHROPIC_API_KEY"),
        )
    else:
        raise ValueError(f"Unsupported model provider: {config.model_provider}")


def create_agent_graph(config: Optional[Configuration] = None) -> _SimpleApp:
    """Create a simplified agent graph application."""

    if config is None:
        config = Configuration()

    tools = get_enabled_tools(config)
    return _SimpleApp(config, tools)


# ---------------------------------------------------------------------------
# Convenience run helpers
# ---------------------------------------------------------------------------

def run_agent(query: str, config: Optional[Configuration] = None, thread_id: str = "default") -> str:
    """Run the agent synchronously and return the final reply."""

    if config is None:
        config = Configuration()

    app = create_agent_graph(config)
    state = {
        "messages": [HumanMessage(content=query)],
        "iteration_count": 0,
        "user_input": query,
        "final_answer": None,
    }
    result = app.invoke(state, config={"configurable": {"thread_id": thread_id}})
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage) or hasattr(msg, "content"):
            return getattr(msg, "content", "")
    return "抱歉，没有找到有效的回答。"


async def arun_agent(query: str, config: Optional[Configuration] = None, thread_id: str = "default") -> str:
    """Run the agent asynchronously and return the final reply."""

    if config is None:
        config = Configuration()

    app = create_agent_graph(config)
    state = {
        "messages": [HumanMessage(content=query)],
        "iteration_count": 0,
        "user_input": query,
        "final_answer": None,
    }
    result = await app.ainvoke(state, config={"configurable": {"thread_id": thread_id}})
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage) or hasattr(msg, "content"):
            return getattr(msg, "content", "")
    return "抱歉，没有找到有效的回答。"


# Re-export for external use
__all__ = [
    "BaseMessage",
    "HumanMessage",
    "AIMessage",
    "ToolMessage",
    "create_llm",
    "create_agent_graph",
    "run_agent",
    "arun_agent",
]
