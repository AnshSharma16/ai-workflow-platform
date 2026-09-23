# AI Workflow Automation Platform

A backend workflow automation platform built with FastAPI, PostgreSQL, SQLAlchemy 2.0, and Docker.

The system allows users to create workflows composed of connected nodes, validate workflow graphs, execute workflows asynchronously, track individual node executions, handle retries, and retrieve execution history.

## Features

- JWT-based authentication
- User and workspace management
- Workspace-based authorization
- Workflow creation and management
- Workflow nodes and edges
- Directed graph validation
- Conditional branching
- Webhook node support
- LLM node support
- Condition node support
- Asynchronous workflow execution
- Background execution
- Per-node execution tracking
- Workflow execution history
- Node execution history
- Retry handling with exponential backoff and jitter
- Execution lifecycle protection
- PostgreSQL persistence
- SQLAlchemy 2.0 async ORM
- Alembic database migrations
- Dockerized API and PostgreSQL
- Automated tests with pytest

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.10 |
| API Framework | FastAPI |
| Server | Uvicorn |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 |
| Validation | Pydantic v2 |
| Migrations | Alembic |
| Authentication | JWT |
| Testing | pytest / pytest-asyncio |
| Containerization | Docker / Docker Compose |

## Architecture

The backend follows a layered architecture:

```text
Client
  │
  ▼
FastAPI Router
  │
  ▼
Service Layer
  │
  ▼
Repository Layer
  │
  ▼
PostgreSQL
```

Workflow execution uses a separate execution and adapter flow:

```text
Workflow Service
      │
      ▼
Node Executor
      │
      ▼
Adapter Factory
      │
      ▼
Node Adapter
      │
      ▼
External Integration
```

The architecture separates HTTP handling, business logic, database access, workflow execution, and external integrations.

## Workflow Model

A workflow is represented as a directed graph containing nodes and edges.

Example:

```text
Trigger
   │
   ▼
Node A
   │
   ▼
Condition
  ├──────── true ────────► Node B
  │
  └──────── false ───────► Node C
```

Nodes represent individual units of work.

Edges define the relationship and execution flow between nodes.

Before execution, the workflow graph is validated to ensure that the execution structure is valid.

## Workflow Execution

When a workflow is executed, an execution record is created and individual node executions are tracked separately.

The workflow execution lifecycle is:

```text
PENDING
   │
   ▼
RUNNING
   │
   ▼
SUCCESS
```

Failed executions follow:

```text
PENDING
   │
   ▼
RUNNING
   │
   ▼
FAILED
```

Execution lifecycle protection prevents an execution that is already in a terminal or active state from being executed again.

For example, an execution that is already:

```text
RUNNING
SUCCESS
FAILED
```

will not be started again by the workflow execution handler.

## Node Execution Tracking

Each workflow node execution is tracked independently.

Node execution records contain information such as:

- Execution status
- Attempt count
- Error information
- Execution result
- Associated workflow execution
- Associated workflow node

This allows individual node execution history to be inspected separately from the overall workflow execution.

## Conditional Branching

Condition nodes can evaluate workflow data and determine which branch should execute.

Example:

```text
Input
  │
  ▼
Condition
  │
  ├── condition = true  ──► Node A
  │
  └── condition = false ─► Node B
```

This allows workflow execution to follow different paths based on runtime data.

## Retry Handling

Node execution supports retry handling through a dedicated retry manager.

Current configuration:

- Maximum attempts: `5`
- Base delay: `0.5 seconds`
- Exponential backoff
- Maximum delay: `30 seconds`
- Jitter: `±25%`

Example:

```text
Attempt 1
   │
   └── failure
          │
          ▼
Attempt 2
   │
   └── failure
          │
          ▼
Attempt 3
   │
   └── success
```

If a node continues to fail after the maximum number of attempts, the node execution is marked as `FAILED` and the workflow execution is also marked as `FAILED`.

## Authentication & Authorization

Protected API endpoints use JWT authentication.

The authentication flow is:

```text
Request
   │
   ▼
JWT Validation
   │
   ▼
Current User
   │
   ▼
Authorization / Ownership Check
   │
   ▼
Service Layer
   │
   ▼
Repository Layer
```

Workspace-owned resources are checked against the authenticated user before access is granted.

This prevents users from accessing or executing resources belonging to another user.

Authentication endpoints remain publicly accessible where required for registration and login.

## Project Structure

```text
ai-workflow-platform/
│
├── backend/
│   │
│   ├── app/
│   │   ├── adapters/
│   │   │   └── ...
│   │   │
│   │   ├── core/
│   │   │   └── ...
│   │   │
│   │   ├── dependencies/
│   │   │   └── ...
│   │   │
│   │   ├── models/
│   │   │   └── ...
│   │   │
│   │   ├── repositories/
│   │   │   └── ...
│   │   │
│   │   ├── routes/
│   │   │   └── ...
│   │   │
│   │   ├── schemas/
│   │   │   └── ...
│   │   │
│   │   ├── services/
│   │   │   └── ...
│   │   │
│   │   └── main.py
│   │
│   ├── alembic/
│   │   └── versions/
│   │
│   ├── tests/
│   │   └── ...
│   │
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   ├── alembic.ini
│   └── .env
│
└── README.md
```

## Database

The application uses PostgreSQL as its primary database.

SQLAlchemy 2.0's asynchronous API is used for database access.

Database schema changes are managed through Alembic migrations.

The Docker Compose setup contains:

```text
API Container
     │
     │ PostgreSQL connection
     ▼
PostgreSQL Container
```

Inside the Docker Compose network, the API connects to PostgreSQL using the database service name rather than `localhost`.

## Running the Application

### Prerequisites

- Docker
- Docker Compose
- Git

### Clone the Repository

```bash
git clone <your-repository-url>
cd ai-workflow-platform/backend
```

### Environment Variables

Create a `.env` file in the backend directory:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/ai_workflow_db
SECRET_KEY=<your-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=true
```

Do not commit the `.env` file or expose the actual `SECRET_KEY`.

### Start the Application

Build and start the containers:

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

## API Documentation

FastAPI automatically generates interactive API documentation.

Swagger UI:

```text
http://localhost:8000/docs
```

OpenAPI schema:

```text
http://localhost:8000/openapi.json
```

The Swagger UI can be used to inspect and interact with the available API endpoints.

## Database Migrations

Check the current migration:

```bash
alembic current
```

Apply all pending migrations:

```bash
alembic upgrade head
```

Create a new migration:

```bash
alembic revision --autogenerate -m "describe change"
```

## Running Tests

Run the complete test suite:

```bash
python -m pytest -q
```

The test suite covers core workflow execution behavior, including:

- Workflow execution
- Node execution
- Successful node execution
- Conditional execution
- Execution lifecycle protection
- Workflow execution history
- Node execution history
- Authorization
- Retry behavior
- Retry success
- Retry exhaustion
- Failure handling

## Design Principles

### Separation of Concerns

HTTP handling, business logic, persistence, workflow execution, and external integrations are kept separate.

### Repository Pattern

Database operations are isolated inside repository classes.

Services interact with repositories instead of embedding database access throughout the application.

### Service Layer

Business logic is handled by service classes.

This includes workflow execution, authorization checks, execution state management, and retry handling.

### Adapter Layer

External node integrations are isolated behind adapters.

The adapter factory selects the appropriate adapter based on the node type.

### Dependency Injection

FastAPI dependency injection is used for database sessions, authentication, and request-scoped dependencies.

### Explicit Execution State

Workflow and node execution state is persisted in the database.

This allows execution history to be queried and prevents completed executions from being processed again.

### Asynchronous I/O

The application uses asynchronous database access and asynchronous execution components where appropriate.

## Current Scope

The project focuses on the backend workflow execution engine and its supporting infrastructure.

The following are intentionally outside the current scope:

- Frontend UI
- Kubernetes
- Redis
- Celery
- Elasticsearch
- Microservice decomposition
- Advanced observability infrastructure
- Complex workflow scheduling

The current implementation focuses on workflow management, graph execution, authorization, persistence, retries, testing, and containerized development.

## Project Status

The following components are implemented:

- Authentication
- JWT authorization
- Workspace management
- Workflow management
- Workflow nodes
- Workflow edges
- Graph validation
- Conditional branching
- Workflow execution
- Background execution
- Retry handling
- Node execution tracking
- Workflow execution history
- Node execution history
- PostgreSQL persistence
- SQLAlchemy async ORM
- Alembic migrations
- Dockerized API
- Dockerized PostgreSQL
- Automated tests

## License

This project is currently intended as a portfolio and engineering project.