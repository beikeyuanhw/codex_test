"""LangGraph代理图形定义

这个模块定义了代理的核心逻辑和工作流程。
"""

import os
from typing import Dict, Any, List, Optional, Annotated
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from .config import Configuration
from .tools import get_enabled_tools


class AgentState(TypedDict):
    """代理状态定义
    
    定义了在图形节点之间传递的状态结构。
    """
    messages: Annotated[List[BaseMessage], add_messages]
    iteration_count: int
    user_input: str
    final_answer: Optional[str]


def create_llm(config: Configuration):
    """根据配置创建LLM实例
    
    Args:
        config: 配置对象
        
    Returns:
        配置好的LLM实例
    """
    if config.model_provider.lower() == "openai":
        return ChatOpenAI(
            model=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    elif config.model_provider.lower() == "anthropic":
        return ChatAnthropic(
            model=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    else:
        raise ValueError(f"不支持的模型提供商: {config.model_provider}")


def create_agent_node(config: Configuration):
    """创建代理节点
    
    Args:
        config: 配置对象
        
    Returns:
        代理节点函数
    """
    # 创建LLM
    llm = create_llm(config)
    
    # 获取启用的工具
    tools = get_enabled_tools(config)
    
    # 绑定工具到LLM
    if tools:
        llm_with_tools = llm.bind_tools(tools)
    else:
        llm_with_tools = llm
    
    # 创建提示模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", config.system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    # 创建链
    chain = prompt | llm_with_tools
    
    def agent_node(state: AgentState) -> Dict[str, Any]:
        """代理节点执行函数"""
        try:
            # 调用LLM
            response = chain.invoke({
                "messages": state["messages"]
            })
            
            # 更新迭代计数
            iteration_count = state.get("iteration_count", 0) + 1
            
            return {
                "messages": [response],
                "iteration_count": iteration_count
            }
        except Exception as e:
            error_message = AIMessage(content=f"抱歉，处理您的请求时出现错误：{str(e)}")
            return {
                "messages": [error_message],
                "iteration_count": state.get("iteration_count", 0) + 1
            }
    
    return agent_node


def should_continue(state: AgentState) -> str:
    """决定是否继续执行的条件函数
    
    Args:
        state: 当前状态
        
    Returns:
        下一个节点的名称
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    # 如果最后一条消息有工具调用，继续执行工具
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    
    # 否则结束
    return END


def create_agent_graph(config: Configuration = None) -> StateGraph:
    """创建代理图形
    
    Args:
        config: 配置对象，如果为None则使用默认配置
        
    Returns:
        编译好的LangGraph图形
    """
    if config is None:
        config = Configuration()
    
    # 创建状态图
    workflow = StateGraph(AgentState)
    
    # 创建节点
    agent_node = create_agent_node(config)
    tools = get_enabled_tools(config)
    
    # 添加节点
    workflow.add_node("agent", agent_node)
    
    if tools:
        # 如果有工具，添加工具节点
        tool_node = ToolNode(tools)
        workflow.add_node("tools", tool_node)
        
        # 添加边
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                END: END
            }
        )
        workflow.add_edge("tools", "agent")
    else:
        # 如果没有工具，直接从agent到结束
        workflow.add_edge(START, "agent")
        workflow.add_edge("agent", END)
    
    # 添加内存检查点（如果启用）
    checkpointer = None
    if config.enable_memory:
        checkpointer = MemorySaver()
    
    # 编译图形
    app = workflow.compile(checkpointer=checkpointer)
    
    return app


def run_agent(query: str, config: Configuration = None, thread_id: str = "default") -> str:
    """运行代理并返回结果
    
    Args:
        query: 用户查询
        config: 配置对象
        thread_id: 线程ID，用于内存管理
        
    Returns:
        代理的回答
    """
    if config is None:
        config = Configuration()
    
    # 创建图形
    app = create_agent_graph(config)
    
    # 准备输入
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "iteration_count": 0,
        "user_input": query,
        "final_answer": None
    }
    
    # 运行图形
    thread_config = {"configurable": {"thread_id": thread_id}} if config.enable_memory else None
    
    try:
        result = app.invoke(initial_state, config=thread_config)
        
        # 提取最后的AI消息
        messages = result["messages"]
        for message in reversed(messages):
            if isinstance(message, AIMessage):
                return message.content
        
        return "抱歉，没有找到有效的回答。"
        
    except Exception as e:
        return f"运行代理时出现错误：{str(e)}"


async def arun_agent(query: str, config: Configuration = None, thread_id: str = "default") -> str:
    """异步运行代理并返回结果
    
    Args:
        query: 用户查询
        config: 配置对象
        thread_id: 线程ID，用于内存管理
        
    Returns:
        代理的回答
    """
    if config is None:
        config = Configuration()
    
    # 创建图形
    app = create_agent_graph(config)
    
    # 准备输入
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "iteration_count": 0,
        "user_input": query,
        "final_answer": None
    }
    
    # 运行图形
    thread_config = {"configurable": {"thread_id": thread_id}} if config.enable_memory else None
    
    try:
        result = await app.ainvoke(initial_state, config=thread_config)
        
        # 提取最后的AI消息
        messages = result["messages"]
        for message in reversed(messages):
            if isinstance(message, AIMessage):
                return message.content
        
        return "抱歉，没有找到有效的回答。"
        
    except Exception as e:
        return f"运行代理时出现错误：{str(e)}"