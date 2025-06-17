class ChatOpenAI:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
    def bind_tools(self, tools):
        return self
    def invoke(self, inputs):
        raise NotImplementedError("ChatOpenAI.invoke should be mocked in tests")
