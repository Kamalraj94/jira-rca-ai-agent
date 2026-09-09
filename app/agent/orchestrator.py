from app.clients.jira_client import JiraClient
from app.clients.llm_client import LLMClient
from app.models import RCAAnalysis

class RCAAgent:
    def __init__(self, jira: JiraClient, llm: LLMClient):
        self.jira = jira
        self.llm = llm

    async def analyze_issue(self, issue_key: str) -> RCAAnalysis:
        defect = await self.jira.get_defect(issue_key)
        return await self.llm.analyze(defect)
