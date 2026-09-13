import pytest
from uuid import uuid4

from app.models.user import User
from app.models.workspace import Workspace
from app.models.workflow import Workflow
from app.models.workflow_edge import WorkflowEdge
from app.models.workflow_execution import ExecutionStatus
from app.models.workflow_node import WorkflowNode
from app.services.workflow_execution_service import (
    WorkflowExecutionService,
)


@pytest.mark.asyncio
async def test_user_cannot_execute_another_users_workflow(
    db_session,
):
    user_a = User(
        email=f"user-a-{uuid4().hex}@example.com",
        username=f"user-a-{uuid4().hex}",
        hashed_password="test",
    )

    user_b = User(
        email=f"user-b-{uuid4().hex}@example.com",
        username=f"user-b-{uuid4().hex}",
        hashed_password="test",
    )

    db_session.add_all([user_a, user_b])
    await db_session.flush()

    workspace_b = Workspace(
        name="User B Workspace",
        user_id=user_b.id,
    )

    db_session.add(workspace_b)
    await db_session.flush()

    workflow = Workflow(
        name="Private Workflow",
        workspace_id=workspace_b.id,
    )

    db_session.add(workflow)
    await db_session.flush()

    service = WorkflowExecutionService(db_session)

    with pytest.raises(PermissionError):
        await service.start_execution(
            workflow.id,
            user_a,
            {"message": "unauthorized"},
        )


@pytest.mark.asyncio
async def test_condition_true_branch(
    db_session,
):
    user = User(
        email=f"user-{uuid4().hex}@example.com",
        username=f"user-{uuid4().hex}",
        hashed_password="test",
    )

    db_session.add(user)
    await db_session.flush()

    workspace = Workspace(
        name="Test Workspace",
        user_id=user.id,
    )

    db_session.add(workspace)
    await db_session.flush()

    workflow = Workflow(
        name="Condition Workflow",
        workspace_id=workspace.id,
    )

    db_session.add(workflow)
    await db_session.flush()

    condition_node = WorkflowNode(
        workflow_id=workflow.id,
        node_type="condition",
        name="Check Amount",
        config={
            "field": "amount",
            "operator": "greater_than",
            "value": 1000,
        },
    )

    true_node = WorkflowNode(
        workflow_id=workflow.id,
        node_type="webhook",
        name="True Node",
        config={},
    )

    false_node = WorkflowNode(
        workflow_id=workflow.id,
        node_type="webhook",
        name="False Node",
        config={},
    )

    db_session.add_all(
        [
            condition_node,
            true_node,
            false_node,
        ]
    )

    await db_session.flush()

    true_edge = WorkflowEdge(
        workflow_id=workflow.id,
        source_node_id=condition_node.id,
        target_node_id=true_node.id,
        branch="true",
    )

    false_edge = WorkflowEdge(
        workflow_id=workflow.id,
        source_node_id=condition_node.id,
        target_node_id=false_node.id,
        branch="false",
    )

    db_session.add_all(
        [
            true_edge,
            false_edge,
        ]
    )

    await db_session.flush()

    service = WorkflowExecutionService(db_session)

    execution = await service.start_execution(
        workflow.id,
        user,
        {"amount": 1500},
    )

    assert execution is not None
    assert execution.status == ExecutionStatus.SUCCESS
    assert execution.output_data == {"amount": 1500}