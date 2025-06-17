class BaseMessage:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls or []

class HumanMessage(BaseMessage):
    pass

class AIMessage(BaseMessage):
    pass

class ToolMessage(BaseMessage):
    pass
