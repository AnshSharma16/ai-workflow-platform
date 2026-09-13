from app.adapters.base import NodeAdapter
from app.adapters.llm import LLMAdapter
from app.adapters.webhook import WebhookAdapter
from app.adapters.condition import ConditionAdapter

class AdapterFactory:

    @staticmethod
    def get_adapter(node_type: str) -> NodeAdapter:
        if node_type == "webhook":
            return WebhookAdapter()

        if node_type == "llm":
            return LLMAdapter()

        if node_type == "condition":
            return ConditionAdapter()

        raise ValueError(
            f"Unsupported node type: {node_type}"
        )