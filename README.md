# jira-rca-ai-agent

# Jira RCA Agent

Fetches a Jira Cloud defect, extracts the configured RCA custom field and latest developer comment,
and asks an internal LLM for structured analysis and retest recommendations.

## Setup

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
copy .env.example .env
```

Edit `.env`. Use an Atlassian email plus API token, not an account password. Never commit `.env`.

## Run

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` and call `POST /api/v1/analyze`:

```json
{"issue_key": "KAN-1"}
```

Or:

```bash
curl -X GET http://127.0.0.1:8000/api/v1/analyze/KAN-1
```

## EYQ API adaptation

The exact internal LLM request and response contract was not supplied. The current adapter assumes an
OpenAI-compatible `messages` request and `choices[0].message.content` response. If EYQ differs, edit only:

- `LLMClient._build_payload()`
- `LLMClient._extract_text()`
- `LLM_AUTH_HEADER` and `LLM_AUTH_PREFIX` in `.env`

## Test

```bash
pytest -q
```

## Security

- Keep Jira and LLM tokens only in environment variables or an approved secret vault.
- This service performs Jira reads only.
- Do not disable TLS verification outside controlled diagnostics.
- Add enterprise authentication and authorization before shared deployment.


## Steps to setup in local 

- Extract the ZIP and open the project directory -

Hit the below commands in terminal 

1. Copy-Item .env.example .env 
2. py -m venv .venv
3. .\.venv\Scripts\Activate.ps1
4. Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass ( only if the abov step is not working )
5. .\.venv\Scripts\Activate.ps1
6. py -m pip install -r requirements.txt
7. py -m uvicorn app.main:app --reload
 
Expected Output : 
Uvicorn running on http://127.0.0.1:8000
Application startup complete

Health Check up URL 
http://127.0.0.1:8000/health

Expected output -> 

{
"status": "UP"
}