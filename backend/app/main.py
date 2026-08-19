from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.workspaces import router as workspace_router
from app.core.exception_handlers import duplicate_email_handler
from app.core.exceptions import DuplicateEmailError


app = FastAPI(
    title="AI Workflow Automation API",
    version="0.1.0",
     exception_handlers={
        DuplicateEmailError: duplicate_email_handler,
    },
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(workspace_router)



@app.get("/")
async def root():
    
    return {
        "message": "AI Workflow Automation API"
    }