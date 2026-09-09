import re
import httpx
from app.config import Settings
from app.exceptions import AgentError
from app.models import DefectContext
from app.utils.adf import adf_to_text

ISSUE_KEY = re.compile(r"^[A-Z][A-Z0-9_]*-\d+$")

class JiraClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def get_defect(self, issue_key: str) -> DefectContext:
        issue_key = issue_key.strip().upper()
        if not ISSUE_KEY.fullmatch(issue_key):
            raise AgentError("Invalid Jira issue key.", 422)

        url = f"{self.settings.jira_base_url.rstrip('/')}/rest/api/3/issue/{issue_key}"
        params = {"fields": f"summary,description,status,priority,comment,{self.settings.jira_rca_field}"}
        try:
            async with httpx.AsyncClient(
                auth=(self.settings.jira_email, self.settings.jira_api_token.get_secret_value()),
                timeout=self.settings.jira_timeout_seconds,
                headers={"Accept": "application/json"},
            ) as client:
                response = await client.get(url, params=params)
        except httpx.RequestError as exc:
            raise AgentError(f"Unable to connect to Jira: {exc}", 502) from exc

        if response.status_code == 401:
            raise AgentError("Jira authentication failed. Check email and API token.", 502)
        if response.status_code == 403:
            raise AgentError("Jira access denied for this issue.", 403)
        if response.status_code == 404:
            raise AgentError(f"Jira issue {issue_key} was not found or is not visible.", 404)
        if response.is_error:
            raise AgentError(f"Jira returned HTTP {response.status_code}.", 502)

        return self._map_issue(response.json())

    def _map_issue(self, payload: dict) -> DefectContext:
        fields = payload.get("fields") or {}
        comments = ((fields.get("comment") or {}).get("comments") or [])
        latest_comment = comments[-1].get("body") if comments else None
        rca_value = fields.get(self.settings.jira_rca_field)
        rca = adf_to_text(rca_value).strip() if isinstance(rca_value, (dict, list)) else str(rca_value or "").strip()

        return DefectContext(
            issue_key=payload.get("key", ""),
            summary=fields.get("summary") or "",
            description=adf_to_text(fields.get("description")).strip(),
            status=(fields.get("status") or {}).get("name", ""),
            priority=(fields.get("priority") or {}).get("name", ""),
            rca=rca,
            developer_comment=adf_to_text(latest_comment).strip(),
        )
