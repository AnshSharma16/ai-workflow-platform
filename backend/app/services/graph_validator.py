from uuid import UUID

from app.models.workflow_edge import WorkflowEdge
from app.models.workflow_node import WorkflowNode


class GraphValidationError(ValueError):
    pass


class GraphValidator:
    def validate(
        self,
        workflow_id: UUID,
        nodes: list[WorkflowNode],
        edges: list[WorkflowEdge],
    ) -> None:
        node_ids = {node.id for node in nodes}

        for node in nodes:
            if node.workflow_id != workflow_id:
                raise GraphValidationError(
                    f"Node {node.id} does not belong to this workflow"
                )

        for edge in edges:
            if edge.workflow_id != workflow_id:
                raise GraphValidationError(
                    f"Edge {edge.id} does not belong to this workflow"
                )

            if edge.source_node_id not in node_ids:
                raise GraphValidationError(
                    f"Source node {edge.source_node_id} not found"
                )

            if edge.target_node_id not in node_ids:
                raise GraphValidationError(
                    f"Target node {edge.target_node_id} not found"
                )

            if edge.source_node_id == edge.target_node_id:
                raise GraphValidationError(
                    f"Self-loop detected on node {edge.source_node_id}"
                )