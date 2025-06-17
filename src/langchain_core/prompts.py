class ChatPromptTemplate:
    def __init__(self, messages):
        self.messages = messages

    @classmethod
    def from_messages(cls, messages):
        return cls(messages)

    def __or__(self, llm):
        class Chain:
            def __init__(self, llm):
                self.llm = llm
            def invoke(self, inputs):
                return self.llm.invoke(inputs)
        return Chain(llm)

class MessagesPlaceholder:
    def __init__(self, variable_name):
        self.variable_name = variable_name
