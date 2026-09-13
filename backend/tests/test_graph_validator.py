from uuid import uuid4

import pytest

from app.models.workflow_edge import WorkflowEdge
from app.models.workflow_node import WorkflowNode
from app.services.graph_validator import (
    GraphValidationError,
    GraphValidator,
)


def make_node(workflow_id):
    return WorkflowNode(
        id=uuid4(),
        workflow_id=workflow_id,
        node_type="llm",
        name="Test Node",
        config={},
    )


def make_edge(workflow_id, source_id, target_id):
    return WorkflowEdge(
        id=uuid4(),
        workflow_id=workflow_id,
        source_node_id=source_id,
        target_node_id=target_id,
    )


def test_valid_graph():
    workflow_id = uuid4()

    node_a = make_node(workflow_id)
    node_b = make_node(workflow_id)

    edge = make_edge(
        workflow_id,
        node_a.id,
        node_b.id,
    )

    GraphValidator().validate(
        workflow_id,
        [node_a, node_b],
        [edge],
    )


def test_missing_target_node():
    workflow_id = uuid4()

    node_a = make_node(workflow_id)
    missing_node_id = uuid4()

    edge = make_edge(
        workflow_id,
        node_a.id,
        missing_node_id,
    )

    with pytest.raises(
        GraphValidationError,
        match="Target node",
    ):
        GraphValidator().validate(
            workflow_id,
            [node_a],
            [edge],
        )


def test_self_loop_rejected():
    workflow_id = uuid4()

    node = make_node(workflow_id)

    edge = make_edge(
        workflow_id,
        node.id,
        node.id,
    )

    with pytest.raises(
        GraphValidationError,
        match="Self-loop",
    ):
        GraphValidator().validate(
            workflow_id,
            [node],
            [edge],
        )