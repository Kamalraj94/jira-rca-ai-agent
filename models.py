from pydantic import BaseModel, Field

class DefectContext(BaseModel):
    issue_key: str
    summary: str = ""
    description: str = ""
    status: str = ""
    priority: str = ""
    rca: str = ""
    developer_comment: str = ""

class RCAAnalysis(BaseModel):
    issue_key: str
    rca: str
    developer_comment: str
    analysis: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    retest_focus: list[str] = Field(default_factory=list)

class AnalyzeRequest(BaseModel):
    issue_key: str = Field(pattern=r"^[A-Z][A-Z0-9_]*-\d+$", examples=["KAN-1"])

class ErrorResponse(BaseModel):
    detail: str
