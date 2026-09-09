from fastapi import APIRouter, Depends
from app.agent.orchestrator import RCAAgent
from app.clients.jira_client import JiraClient
from app.clients.llm_client import LLMClient
from app.config import Settings, get_settings
from app.models import AnalyzeRequest, RCAAnalysis

router = APIRouter(tags=["RCA Agent"])

def get_agent(settings: Settings = Depends(get_settings)) -> RCAAgent:
    return RCAAgent(JiraClient(settings), LLMClient(settings))

@router.post("/analyze", response_model=RCAAnalysis)
async def analyze(request: AnalyzeRequest, agent: RCAAgent = Depends(get_agent)) -> RCAAnalysis:
    return await agent.analyze_issue(request.issue_key)

@router.get("/analyze/{issue_key}", response_model=RCAAnalysis)
async def analyze_by_key(issue_key: str, agent: RCAAgent = Depends(get_agent)) -> RCAAnalysis:
    return await agent.analyze_issue(issue_key)
