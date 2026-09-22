# AI Workflow Platform

A production-oriented workflow automation backend inspired by platforms such as n8n, Zapier, and Make.

The platform allows users to create workflows composed of connected nodes, execute those workflows asynchronously, track execution history, and handle node failures with retry logic.

## 🚀 Tech Stack

* **Python 3.10**
* **FastAPI**
* **PostgreSQL**
* **SQLAlchemy 2.0 (Async)**
* **Pydantic v2**
* **Alembic**
* **Docker / Docker Compose**
* **JWT Authentication**
* **pytest / pytest-asyncio**

## 🏗️ Architecture

The backend follows a layered architecture:

```text
Router
   ↓
Service
   ↓
Repository
   ↓
PostgreSQL
```

External integrations are isolated through an adapter layer.

```text
API Request
    ↓
FastAPI Router
    ↓
Service Layer
    ↓
Repository Layer
    ↓
PostgreSQL

Workflow Execution
    ↓
Node Executor
    ↓
Adapter Factory
    ↓
Node Adapter
```

## ⚙️ Core Features

* User authentication with JWT
* Workspace-based authorization
* Workflow creation and management
* Workflow nodes and edges
* Graph-based workflow execution
* Conditional branching
* Background workflow execution
* Workflow execution history
* Per-node execution history
* Execution lifecycle management
* Retry handling with bounded backoff
* PostgreSQL persistence
* Async SQLAlchemy
* Database migrations with Alembic
* API documentation through Swagger/OpenAPI

## 🔄 Workflow Execution

A workflow consists of nodes connected through directed edges.

Example:

```text
        ┌──────────────┐
        │ Start/Webhook│
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │  Condition   │
        └──────┬───────┘
          ┌────┴────┐
          ▼         ▼
       ┌──────┐  ┌──────┐
       │ True │  │False │
       │ Node │  │ Node │
       └──────┘  └──────┘
```

Execution state follows:

```text
PENDING → RUNNING → SUCCESS
                  ↘ FAILED
```

Completed, failed, or already-running executions cannot be started again.

## 🔁 Retry Handling

Node execution supports bounded retry handling for failures.

The retry mechanism includes:

* Configurable maximum attempts
* Exponential backoff
* Maximum backoff limit
* Jitter to avoid synchronized retries
* Per-node execution tracking
* Persistent failure information

## 🗄️ Database

PostgreSQL stores:

* Users
* Workspaces
* Workflows
* Workflow nodes
* Workflow edges
* Workflow executions
* Node executions

Database schema changes are managed through Alembic migrations.

## 🧪 Testing

Run the complete test suite:

```bash
python -m pytest -v
```

Run workflow execution tests:

```bash
python -m pytest tests/test_workflow_execution.py -v
```

## 🐳 Running Locally

Clone the repository:

```bash
git clone <repository-url>
cd ai-workflow-platform
```

Start PostgreSQL:

```bash
docker compose up -d
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Run database migrations:

```bash
alembic upgrade head
```

Start the API:

```bash
uvicorn app.main:app --reload
```

The API documentation is available through FastAPI's Swagger UI.

## 📌 Project Status

Currently focused on completing the workflow execution engine, failure/retry handling, automated testing, and deployment.

## 🎯 Engineering Goals

This project is built to demonstrate practical backend engineering skills including:

* Async Python
* REST API development
* Database design
* Repository/service architecture
* Authentication and authorization
* Background processing
* Workflow execution
* Failure handling and retries
* Automated testing
* Containerization
* Production-oriented system design
