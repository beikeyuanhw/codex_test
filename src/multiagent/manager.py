"""Multi-agent manager module.

This module provides a ``MultiAgentManager`` class that can
instantiate multiple agent graphs and route messages between them.
"""

from typing import Dict, List

from langchain_core.messages import AIMessage, HumanMessage, BaseMessage

from agent import Configuration, create_agent_graph


class MultiAgentManager:
    """Manager for coordinating multiple agents."""

    def __init__(self, configs: Dict[str, Configuration]):
        """Create manager with a mapping of agent name to ``Configuration``."""
        self.graphs = {name: create_agent_graph(cfg) for name, cfg in configs.items()}
        self.histories: Dict[str, List[BaseMessage]] = {name: [] for name in configs}

    def send_to_agent(self, agent_name: str, message: str) -> str:
        """Send a message to a specific agent and get its reply."""
        history = self.histories[agent_name]
        state = {
            "messages": history + [HumanMessage(content=message)],
            "iteration_count": 0,
            "user_input": message,
            "final_answer": None,
        }
        result = self.graphs[agent_name].invoke(state)
        history.append(HumanMessage(content=message))
        history.extend(result["messages"])
        reply = ""
        for msg in reversed(result["messages"]):
            if isinstance(msg, AIMessage):
                reply = msg.content
                break
        return reply

    def relay_message(self, sender: str, receiver: str, message: str) -> str:
        """Relay a message from one agent to another."""
        reply = self.send_to_agent(receiver, message)
        # Receiver's reply becomes the next input for the sender
        self.histories[sender].append(HumanMessage(content=reply))
        return reply
