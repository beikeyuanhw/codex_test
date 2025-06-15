"""LangGraph代理项目主入口

这个文件提供了多种方式来运行和测试代理：
1. 命令行交互模式
2. FastAPI Web服务
3. 单次查询模式
"""

import os
import asyncio
from typing import Optional
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from agent import create_agent_graph, run_agent, arun_agent, Configuration

# 加载环境变量
load_dotenv()


class QueryRequest(BaseModel):
    """查询请求模型"""
    query: str
    thread_id: Optional[str] = "default"
    config: Optional[dict] = None


class QueryResponse(BaseModel):
    """查询响应模型"""
    answer: str
    thread_id: str


# 创建FastAPI应用
app = FastAPI(
    title="LangGraph Agent API",
    description="基于LangGraph构建的智能代理API服务",
    version="0.1.0"
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用LangGraph代理API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """查询代理"""
    try:
        # 创建配置
        config = Configuration()
        if request.config:
            # 更新配置
            for key, value in request.config.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        
        # 运行代理
        answer = await arun_agent(
            query=request.query,
            config=config,
            thread_id=request.thread_id
        )
        
        return QueryResponse(
            answer=answer,
            thread_id=request.thread_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/config")
async def get_default_config():
    """获取默认配置"""
    config = Configuration()
    return config.dict()


def interactive_mode():
    """交互模式"""
    print("🤖 LangGraph代理交互模式")
    print("输入 'quit' 或 'exit' 退出")
    print("输入 'config' 查看当前配置")
    print("-" * 50)
    
    # 创建默认配置
    config = Configuration()
    thread_id = "interactive_session"
    
    while True:
        try:
            user_input = input("\n👤 您: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("👋 再见！")
                break
            
            if user_input.lower() == 'config':
                print("\n📋 当前配置:")
                for key, value in config.dict().items():
                    print(f"  {key}: {value}")
                continue
            
            if not user_input:
                continue
            
            print("\n🤖 代理正在思考...")
            
            # 运行代理
            answer = run_agent(
                query=user_input,
                config=config,
                thread_id=thread_id
            )
            
            print(f"\n🤖 代理: {answer}")
            
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")


def single_query_mode(query: str):
    """单次查询模式"""
    print(f"🤖 处理查询: {query}")
    
    config = Configuration()
    answer = run_agent(query, config)
    
    print(f"\n📝 回答: {answer}")


def start_server(host: str = "localhost", port: int = 8000):
    """启动Web服务器"""
    print(f"🚀 启动LangGraph代理API服务器")
    print(f"📍 地址: http://{host}:{port}")
    print(f"📚 API文档: http://{host}:{port}/docs")
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="LangGraph代理项目")
    parser.add_argument(
        "--mode",
        choices=["interactive", "server", "query"],
        default="interactive",
        help="运行模式"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="单次查询内容（仅在query模式下使用）"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="服务器主机地址（仅在server模式下使用）"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="服务器端口（仅在server模式下使用）"
    )
    
    args = parser.parse_args()
    
    if args.mode == "interactive":
        interactive_mode()
    elif args.mode == "server":
        start_server(args.host, args.port)
    elif args.mode == "query":
        if not args.query:
            print("❌ 错误: 在query模式下必须提供--query参数")
        else:
            single_query_mode(args.query)