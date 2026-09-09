import json
from typing import Any
import httpx
from app.config import Settings
from app.exceptions import AgentError
from app.models import DefectContext, RCAAnalysis
from app.agent.prompts import SYSTEM_PROMPT, build_user_prompt

class LLMClient:
    """Adapter for the internal LLM.

    The default body and response parser are OpenAI-compatible. If the EYQ API
    contract differs, change only _build_payload() and _extract_text().
    """
    def __init__(self, settings: Settings):
        self.settings = settings

    async def analyze(self, defect: DefectContext) -> RCAAnalysis:
        print("mock_llm_mode =", self.settings.mock_llm_mode)
        if self.settings.mock_llm_mode:
            # Return a mock response for testing purposes
            return RCAAnalysis(
                issue_key=defect.issue_key,
                rca=defect.rca,
                developer_comment=defect.developer_comment,
                analysis=[
                    "The defect appears to be related to insufficient tester knowledge.",
                    "Developer has confirmed that a fix has been deployed and is ready for retesting.",
                    "The defect should be validated through both functional and regression testing."
                ],
                recommendations=[
                    "Conduct tester knowledge sharing sessions.",
                    "Review login functionality test coverage.",
                    "Update test case review checklist.",
                      "Include RCA findings in future test planning."
                ],
                retest_focus=[
                    "Valid login scenario.",
                    "Invalid username scenario.",
                    "Invalid password scenario.",
                    "Login error message validation."
                ],)
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        token = self.settings.llm_api_token.get_secret_value()
        prefix = self.settings.llm_auth_prefix.strip()
        headers[self.settings.llm_auth_header] = f"{prefix} {token}".strip()

        try:
            async with httpx.AsyncClient(
                timeout=self.settings.llm_timeout_seconds,
                verify=self.settings.llm_verify_ssl,
            ) as client:
                response = await client.post(
                    self.settings.llm_api_url,
                    headers=headers,
                    json=self._build_payload(defect),
                )
        except httpx.RequestError as exc:
            raise AgentError(f"Unable to connect to the internal LLM: {exc}", 502) from exc

        if response.status_code in (401, 403):
            raise AgentError("Internal LLM authentication or authorization failed.", 502)
        if response.is_error:
            raise AgentError(f"Internal LLM returned HTTP {response.status_code}: {response.text[:300]}", 502)

        text = self._extract_text(response.json())
        try:
            data = json.loads(self._strip_code_fence(text))
            return RCAAnalysis(issue_key=defect.issue_key, **data)
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            raise AgentError("The LLM response was not valid RCAAnalysis JSON.", 502) from exc

    def _build_payload(self, defect: DefectContext) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(defect)},
            ],
            "temperature": 0.1,
        }
        if self.settings.llm_model:
            payload["model"] = self.settings.llm_model
        return payload

    @staticmethod
    def _extract_text(payload: dict[str, Any]) -> str:
        try:
            return payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AgentError("Unknown LLM response format. Update LLMClient._extract_text().", 502) from exc

    @staticmethod
    def _strip_code_fence(value: str) -> str:
        value = value.strip()
        if value.startswith("```"):
            lines = value.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            return "\n".join(lines).strip()
        return value
