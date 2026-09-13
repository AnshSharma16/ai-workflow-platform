from typing import Any
from app.adapters.factory import AdapterFactory
from app.models.workflow_node import WorkflowNode

class NodeExecutor:

    async def execute(
        self,
        node: WorkflowNode,
        input_data: dict[str, Any],
    ) -> dict[str, Any]:

        adapter = AdapterFactory.get_adapter(
            node.node_type
        )

        return await adapter.execute(
            node.config,
            input_data,
        )