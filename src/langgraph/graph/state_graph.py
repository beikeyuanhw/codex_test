START = "start"
END = "end"

class StateGraph:
    def __init__(self, state_schema=None):
        self.nodes = {}
        self.edges = {}
        self.cond_edges = {}

    def add_node(self, name, func):
        self.nodes[name] = func

    def add_edge(self, src, dest):
        self.edges[src] = dest

    def add_conditional_edges(self, src, cond_fn, mapping):
        self.cond_edges[src] = (cond_fn, mapping)

    def compile(self, checkpointer=None):
        graph = self
        class App:
            def __init__(self, graph):
                self._graph = graph
            def get_graph(self):
                return self._graph
            def _run(self, state):
                current = START
                while True:
                    if current == START:
                        current = graph.edges.get(START)
                        continue
                    func = graph.nodes[current]
                    res = func(state)
                    if res:
                        state.update(res)
                    if current in graph.cond_edges:
                        cond_fn, mapping = graph.cond_edges[current]
                        nxt = mapping.get(cond_fn(state), END)
                    else:
                        nxt = graph.edges.get(current, END)
                    if nxt == END:
                        break
                    current = nxt
                return state
            def invoke(self, state, config=None):
                return self._run(state)
            async def ainvoke(self, state, config=None):
                return self._run(state)
        return App(graph)
