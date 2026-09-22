import pytest
from uuid import uuid4

from app.models.user import User
from app.models.workspace import Workspace
from app.models.workflow import Workflow
from app.models.workflow_edge import WorkflowEdge
from app.models.workflow_execution import ExecutionStatus
from app.models.node_execution import NodeExecutionStatus
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
    assert execution.status == ExecutionStatus.PENDING

    await service._execute_workflow(execution.id)

    updated_execution = await service.execution_repository.get_by_id(
        execution.id
    )

    assert updated_execution is not None
    assert updated_execution.status == ExecutionStatus.SUCCESS
    assert updated_execution.output_data == {"amount": 1500}

@pytest.mark.asyncio
async def test_does_not_execute_completed_execution(db_session):
    user = User(
        email=f"user-{uuid4().hex}@example.com",
        username=f"user-{uuid4().hex}",
        hashed_password="testing",
    )

    db_session.add(user)
    await db_session.flush()

    workspace = Workspace(
        name="Test Workspace01",
        user_id=user.id,
    )

    db_session.add(workspace)
    await db_session.flush()

    workflow = Workflow(
        name="Workflow01",
        workspace_id=workspace.id,
    )

    db_session.add(workflow)
    await db_session.flush()

    service = WorkflowExecutionService(db_session)

    execution = await service.start_execution(
        workflow.id,
        user,
        {},
    )

    assert execution is not None
    assert execution.status == ExecutionStatus.PENDING

    await service.execution_repository.update_status(
        execution,
        ExecutionStatus.SUCCESS,
    )

    assert execution.status == ExecutionStatus.SUCCESS

    await service._execute_workflow(execution.id)

    updated_execution = await service.execution_repository.get_by_id(
        execution.id
    )

    assert updated_execution.status == ExecutionStatus.SUCCESS


@pytest.mark.asyncio
async def test_does_not_execute_running_execution(db_session):
    user = User(
        email=f"user-{uuid4().hex}@example.com",
        username=f"user-{uuid4().hex}",
        hashed_password="testing",
    )

    db_session.add(user)
    await db_session.flush()

    workspace = Workspace(
        name="Test Workspace01",
        user_id=user.id,
    )

    db_session.add(workspace)
    await db_session.flush()

    workflow = Workflow(
        name="Workflow01",
        workspace_id=workspace.id,
    )

    db_session.add(workflow)
    await db_session.flush()

    service = WorkflowExecutionService(db_session)

    execution = await service.start_execution(
        workflow.id,
        user,
        {},
    )

    assert execution is not None
    assert execution.status == ExecutionStatus.PENDING

    await service.execution_repository.update_status(
        execution,
        ExecutionStatus.RUNNING,
    )

    assert execution.status == ExecutionStatus.RUNNING

    await service._execute_workflow(execution.id)

    updated_execution = await service.execution_repository.get_by_id(
        execution.id
    )

    assert updated_execution.status == ExecutionStatus.RUNNING

@pytest.mark.asyncio
async def test_does_not_execute_failed_execution(db_session):
    user = User(
    email=f"user-{uuid4().hex}@example.com",
    username=f"user-{uuid4().hex}",
    hashed_password="testing",
    )

    db_session.add(user)
    await db_session.flush()

    workspace = Workspace(
        name="Test Workspace01",
        user_id=user.id,
    )

    db_session.add(workspace)
    await db_session.flush()

    workflow = Workflow(
        name="Workflow01",
        workspace_id=workspace.id,
    )

    db_session.add(workflow)
    await db_session.flush()

    service = WorkflowExecutionService(db_session)

    execution = await service.start_execution(
        workflow.id,
        user,
        {},
    )

    assert execution is not None
    assert execution.status == ExecutionStatus.PENDING

    await service.execution_repository.update_status(
        execution,
        ExecutionStatus.FAILED,
    )

    assert execution.status == ExecutionStatus.FAILED

    await service._execute_workflow(execution.id)

    updated_execution = await service.execution_repository.get_by_id(
        execution.id
    )

    assert updated_execution.status == ExecutionStatus.FAILED

@pytest.mark.asyncio
async def test_successful_node_execution(db_session):
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

    webhook_node = WorkflowNode(
        workflow_id=workflow.id,
        node_type="webhook",
        name="Test Webhook",
        config={},
    )

    db_session.add(webhook_node)
    await db_session.flush()

    service = WorkflowExecutionService(db_session)

    execution = await service.start_execution(
        workflow.id,
        user,
        {},
    )

    assert execution is not None
    assert execution.status == ExecutionStatus.PENDING
    await service._execute_workflow(execution.id)

    node_executions = await service.list_node_executions(
        execution.id,
        user,
    )
    assert len(node_executions) == 1
    node_execution = node_executions[0]

    assert node_execution.status == NodeExecutionStatus.SUCCESS

@pytest.mark.asyncio
async def test_lists_workflow_executions(db_session):
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

    service = WorkflowExecutionService(db_session)

    execution1 = await service.start_execution(
        workflow.id,
        user,
        {},
    )

    execution2 = await service.start_execution(
        workflow.id,
        user,
        {},
    )

    executions = await service.list_for_workflow(
    workflow.id,
    user,
    )

    assert len(executions) == 2

    assert executions[0].workflow_id == workflow.id
    assert executions[1].workflow_id == workflow.id

@pytest.mark.asyncio
async def test_lists_node_executions(db_session):
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

    service = WorkflowExecutionService(db_session)

    execution = await service.start_execution(
        workflow.id,
        user,
        {},
    )

    node1 = WorkflowNode(
        workflow_id=workflow.id,
        node_type="webhook",
        name="Test Webhook1",
        config={},
    )

    node2 = WorkflowNode(
        workflow_id=workflow.id,
        node_type="webhook",
        name="Test Webhook2",
        config={},
    )

    db_session.add_all([node1, node2])
    await db_session.flush()


    edge = WorkflowEdge(
    workflow_id=workflow.id,
    source_node_id=node1.id,
    target_node_id=node2.id,
    )
    db_session.add(edge)
    await db_session.flush()

    assert execution is not None
    assert execution.status == ExecutionStatus.PENDING
    await service._execute_workflow(execution.id)

    node_executions = await service.list_node_executions(
        execution.id,
        user,
    )
    assert len(node_executions) == 2
    node_execution1 = node_executions[0]
    node_execution2 = node_executions[1]

    assert node_execution1.status == NodeExecutionStatus.SUCCESS
    assert node_execution2.status == NodeExecutionStatus.SUCCESS

    assert node_executions[0].node_id == node1.id
    assert node_executions[1].node_id == node2.id
