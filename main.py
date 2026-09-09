from fastapi import FastAPI
from app.api.routes import router
from app.exceptions import AgentError, agent_error_handler

app = FastAPI(title="Jira RCA Agent", version="1.0.0")
app.add_exception_handler(AgentError, agent_error_handler)
app.include_router(router, prefix="/api/v1")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "UP"}
