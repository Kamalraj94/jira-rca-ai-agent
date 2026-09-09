from fastapi import Request
from fastapi.responses import JSONResponse

class AgentError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

async def agent_error_handler(_: Request, exc: AgentError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})
