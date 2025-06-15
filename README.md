# LangGraph Agent Project

基于 [LangGraph](https://github.com/langchain-ai/langgraph) 构建的智能代理项目，提供了一个完整的、可扩展的框架来构建有状态的AI代理工作流。

## 🌟 特性

- **🔧 模块化设计**: 清晰的项目结构，易于扩展和维护
- **🛠️ 丰富的工具集**: 内置天气查询、网络搜索、计算器等工具
- **🧠 智能记忆**: 支持短期和长期记忆，维持对话上下文
- **⚙️ 灵活配置**: 可配置的模型、工具和执行参数
- **🌐 多种接口**: 支持命令行、Web API和编程接口
- **🔄 异步支持**: 支持异步执行，提高性能
- **🎯 生产就绪**: 包含完整的测试套件和部署配置

## 📁 项目结构

```
langgraph-agent-project/
├── src/
│   ├── agent/
│   │   ├── __init__.py          # 包初始化
│   │   ├── config.py            # 配置管理
│   │   ├── graph.py             # 核心图形定义
│   │   └── tools.py             # 工具定义
│   └── main.py                  # 主应用入口
├── examples/
│   └── basic_usage.py           # 使用示例
├── tests/
│   └── test_agent.py            # 测试文件
├── docs/                        # 文档目录
├── requirements.txt             # Python依赖
├── pyproject.toml              # 项目配置
├── langgraph.json              # LangGraph Studio配置
├── .env.example                # 环境变量模板
└── README.md                   # 项目说明
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <your-repo-url>
cd langgraph-agent-project

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -e .
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，添加你的API密钥
# OPENAI_API_KEY=sk-your_openai_api_key_here
# LANGSMITH_API_KEY=lsv2_your_langsmith_api_key_here  # 可选
```

### 3. 运行代理

#### 交互模式
```bash
python src/main.py --mode interactive
```

#### Web API服务
```bash
python src/main.py --mode server
# 访问 http://localhost:8000/docs 查看API文档
```

#### 单次查询
```bash
python src/main.py --mode query --query "你好，请介绍一下你自己"
```

### 4. 使用LangGraph Studio（推荐）

```bash
# 安装LangGraph CLI
pip install "langgraph-cli[inmem]"

# 启动开发服务器
langgraph dev

# 在浏览器中打开LangGraph Studio进行可视化调试
```

## 🛠️ 核心组件

### 配置管理 (Configuration)

```python
from agent import Configuration

# 创建自定义配置
config = Configuration(
    model_provider="openai",
    model_name="gpt-4o-mini",
    temperature=0.1,
    enable_weather_tool=True,
    enable_search_tool=True,
    enable_calculator_tool=True,
    enable_memory=True
)
```

### 工具系统

项目内置了三个基本工具：

1. **天气查询工具** (`get_weather`): 获取城市天气信息
2. **网络搜索工具** (`search_web`): 搜索网络信息
3. **计算器工具** (`calculate`): 执行数学计算

### 代理图形

基于LangGraph构建的状态图，支持：
- 工具调用和响应
- 条件分支
- 循环执行
- 状态管理

## 📚 使用示例

### 基本使用

```python
from agent import run_agent, Configuration

# 使用默认配置
config = Configuration()
result = run_agent("北京今天天气怎么样？", config)
print(result)
```

### 异步使用

```python
import asyncio
from agent import arun_agent, Configuration

async def main():
    config = Configuration()
    result = await arun_agent("计算2的10次方", config)
    print(result)

asyncio.run(main())
```

### 自定义配置

```python
from agent import Configuration, run_agent

# 创建专门用于数学计算的配置
math_config = Configuration(
    system_prompt="你是一个数学专家，专门帮助用户解决数学问题。",
    enable_weather_tool=False,
    enable_search_tool=False,
    enable_calculator_tool=True,
    temperature=0.0
)

result = run_agent("请计算圆周率乘以半径为5的圆的面积", math_config)
print(result)
```

### Web API使用

```python
import requests

# 启动服务器后
response = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "你好，请介绍一下你自己",
        "thread_id": "my_session",
        "config": {
            "temperature": 0.7,
            "enable_memory": True
        }
    }
)

print(response.json())
```

## 🧪 测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 运行测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_agent.py::TestConfiguration -v
```

## 🔧 扩展开发

### 添加新工具

1. 在 `src/agent/tools.py` 中定义新工具：

```python
from langchain_core.tools import tool

@tool
def my_custom_tool(input_param: str) -> str:
    """我的自定义工具描述
    
    Args:
        input_param: 输入参数描述
        
    Returns:
        工具执行结果
    """
    # 工具逻辑
    return f"处理结果: {input_param}"
```

2. 在配置中添加工具开关：

```python
# 在 config.py 的 Configuration 类中添加
enable_my_tool: bool = Field(
    default=True,
    description="是否启用我的自定义工具"
)
```

3. 在 `get_enabled_tools` 函数中注册工具。

### 自定义模型提供商

在 `src/agent/graph.py` 的 `create_llm` 函数中添加新的模型提供商支持。

### 修改代理逻辑

在 `src/agent/graph.py` 中修改 `create_agent_graph` 函数来自定义代理的工作流程。

## 📊 监控和调试

### LangSmith集成

设置环境变量启用LangSmith追踪：

```bash
LANGSMITH_API_KEY=your_api_key
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=your_project_name
```

### LangGraph Studio

LangGraph Studio提供了可视化的调试界面，可以：
- 查看代理执行流程
- 调试状态转换
- 修改和重放执行
- 分析性能指标

## 🚀 部署

### Docker部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY .env .

EXPOSE 8000
CMD ["python", "src/main.py", "--mode", "server", "--host", "0.0.0.0"]
```

### 云平台部署

项目支持部署到各种云平台，如：
- AWS Lambda
- Google Cloud Run
- Azure Container Instances
- Heroku

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - 提供了强大的LLM应用开发框架
- [LangGraph](https://github.com/langchain-ai/langgraph) - 提供了状态图编排能力
- [FastAPI](https://fastapi.tiangolo.com/) - 提供了现代化的Web API框架

## 📞 支持

如果你有任何问题或建议，请：

1. 查看 [文档](docs/)
2. 搜索 [Issues](../../issues)
3. 创建新的 [Issue](../../issues/new)
4. 联系维护者

---

**Happy Coding! 🎉**