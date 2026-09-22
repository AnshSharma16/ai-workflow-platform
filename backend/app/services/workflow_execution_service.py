from uuid import UUID
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import AsyncSessionLocal

from app.models.node_execution import (
    NodeExecution,
    NodeExecutionStatus,
)
from app.models.user import User
from app.models.workflow_execution import (
    ExecutionStatus,
    WorkflowExecution,
)
from app.repositories.node_execution_repository import (
    NodeExecutionRepository,
)
from app.repositories.workflow_edge_repository import (
    WorkflowEdgeRepository,
)
from app.repositories.workflow_execution_repository import (
    WorkflowExecutionRepository,
)
from app.repositories.workflow_node_repository import (
    WorkflowNodeRepository,
)
from app.repositories.workflow_repository import (
    WorkflowRepository,
)
from app.repositories.workspace_repository import (
    WorkspaceRepository,
)
from app.services.graph_validator import GraphValidator
from app.services.node_executor import NodeExecutor
from app.services.retry_manager import RetryManager

async def run_workflow_in_background(
    execution_id: UUID,
) -> None:
    async with AsyncSessionLocal() as db:
        service = WorkflowExecutionService(db)
        await service._execute_workflow(execution_id)

class WorkflowExecutionService:
    def __init__(self, session: AsyncSession) -> None:
        
        
        self.workspace_repository = WorkspaceRepository(session)
        self.workflow_repository = WorkflowRepository(session)
        self.node_repository = WorkflowNodeRepository(session)
        self.edge_repository = WorkflowEdgeRepository(session)
        self.execution_repository = WorkflowExecutionRepository(session)
        self.node_execution_repository = NodeExecutionRepository(session)
        self.graph_validator = GraphValidator()
        self.node_executor = NodeExecutor()
        self.retry_manager=RetryManager()

    async def start_execution(
        self,
        workflow_id: UUID,
        current_user: User,
        input_data: dict | None = None,
    ) -> WorkflowExecution | None:

        workflow = await self.workflow_repository.get_by_id(
            workflow_id
        )

        if workflow is None:
            return None

        workspace = await self.workspace_repository.get_by_id(
            workflow.workspace_id
        )

        if workspace is None:
            return None

        if workspace.user_id != current_user.id:
            raise PermissionError(
                "You are not allowed to execute this workflow"
            )

        nodes = await self.node_repository.get_by_workflow_id(
            workflow_id
        )

        edges = await self.edge_repository.get_by_workflow_id(
            workflow_id
        )

        self.graph_validator.validate(
            workflow_id,
            nodes,
            edges,
        )

        execution = WorkflowExecution(
            workflow_id=workflow_id,
            status=ExecutionStatus.PENDING,
            input_data=input_data,
        )

        execution = await self.execution_repository.create(
            execution
        )

        return execution

    async def _execute_workflow(
        self,
        execution_id: UUID,        
    ) -> None:

        execution = await self.execution_repository.get_by_id(
        execution_id
    )

        if execution is None:
            return

        if execution.status != ExecutionStatus.PENDING:
            return

        nodes = await self.node_repository.get_by_workflow_id(
            execution.workflow_id
        )

        edges = await self.edge_repository.get_by_workflow_id(
            execution.workflow_id
        )

        execution.status = ExecutionStatus.RUNNING

        await self.execution_repository.update_status(
            execution,
            ExecutionStatus.RUNNING,
        )

        try:
            target_node_ids = {
                edge.target_node_id
                for edge in edges
            }

            start_nodes = [
                node
                for node in nodes
                if node.id not in target_node_ids
            ]

            if not start_nodes:
                raise ValueError(
                    "Workflow has no starting node"
                )

            current_node = start_nodes[0]
            current_data = execution.input_data or {}

            while current_node:

                node_input = current_data

                node_execution = NodeExecution(
                    execution_id=execution.id,
                    node_id=current_node.id,
                    status=NodeExecutionStatus.PENDING,
                    input_data=node_input,
                )

                node_execution = (
                    await self.node_execution_repository.create(
                        node_execution
                    )
                )

                await self.node_execution_repository.update_status(
                    node_execution,
                    NodeExecutionStatus.RUNNING,
                )

                attempt =1 

                while True:

                    try:
                        output_data = await self.node_executor.execute(
                            current_node,
                            node_input,
                        )

                        await self.node_execution_repository.update_status(
                            node_execution,
                            NodeExecutionStatus.SUCCESS,
                            output_data=output_data,
                        )

                        break

                    except Exception as exc:
                        if self.retry_manager.should_retry(attempt):
                            delay=self.retry_manager.get_delay(attempt)
                            await asyncio.sleep(delay)
                            attempt+=1
                            node_execution.attempt=attempt
                            continue


                        
                        await self.node_execution_repository.update_status(
                            node_execution,
                            NodeExecutionStatus.FAILED,
                            error_message=str(exc),
                        )
                        raise

                outgoing_edges = [
                    edge
                    for edge in edges
                    if edge.source_node_id == current_node.id
                ]

                if not outgoing_edges:
                    current_data = output_data
                    break

                if current_node.node_type == "condition":

                    branch = (
                        "true"
                        if output_data.get("result") is True
                        else "false"
                    )

                    next_edge = next(
                        (
                            edge
                            for edge in outgoing_edges
                            if edge.branch == branch
                        ),
                        None,
                    )

                    if next_edge is None:
                        raise ValueError(
                            f"No '{branch}' branch found "
                            "for condition node"
                        )

                    # Condition decides the route,
                    # but does not replace workflow data.
                    current_data = node_input

                else:
                    next_edge = outgoing_edges[0]

                    # Normal nodes pass their output forward.
                    current_data = output_data

                current_node = next(
                    (
                        node
                        for node in nodes
                        if node.id == next_edge.target_node_id
                    ),
                    None,
                )

            execution.output_data = current_data
            execution.status = ExecutionStatus.SUCCESS

        except Exception as exc:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = str(exc)

        await self.execution_repository.update_status(
            execution,
            execution.status,
            execution.error_message,
        )

        return None


    async def list_for_workflow(
        self,
        workflow_id:UUID,
        current_user:User,
    )->list[WorkflowExecution] | None:

        workflow=await self.workflow_repository.get_by_id(workflow_id)

        if workflow is None:
            return None
        
        workspace=await self.workspace_repository.get_by_id(workflow.workspace_id)

        if workspace is None:
            return None 
        
        if workspace.user_id!=current_user.id:
            raise PermissionError("You're not authorised")

        return await self.execution_repository.get_by_workflow_id(
            workflow_id
        )

    async def get_execution(
    self,
    execution_id: UUID,
    current_user: User,
) -> WorkflowExecution | None:

        execution=await self.execution_repository.get_by_id(execution_id)

        if execution is None:
            return None
        
        workflow=await self.workflow_repository.get_by_id(execution.workflow_id)

        if workflow is None:
            return None 
        
        workspace=await self.workspace_repository.get_by_id(workflow.workspace_id)

        if workspace is None:
            return None 
        
        if workspace.user_id!=current_user.id:
            raise PermissionError("You're not authorised")

        return execution


    async def list_node_executions(
    self,
    execution_id: UUID,
    current_user: User,
) -> list[NodeExecution] | None:

        execution=await self.execution_repository.get_by_id(execution_id)

        if execution is None:
            return None
        
        workflow=await self.workflow_repository.get_by_id(execution.workflow_id)

        if workflow is None:
            return None 
        
        workspace=await self.workspace_repository.get_by_id(workflow.workspace_id)

        if workspace is None:
            return None 
        
        if workspace.user_id!=current_user.id:
            raise PermissionError("You're not authorised")

        return await self.node_execution_repository.get_by_execution_id(
            execution_id
        )