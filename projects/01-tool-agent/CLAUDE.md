# CLAUDE.md – Tool Agent

Lernprojekt. Der Nutzer ist Junior-Developer: erkläre Änderungen kurz und
verständlich, und ändere nur, worum gebeten wurde.

## Befehle
- Tests: `uv run pytest`
- Lint: `uv run ruff check .`
- CLI: `uv run python -m tool_agent.agent "Frage"`
- API: `uv run uvicorn tool_agent.api:app --reload`

## Struktur
- `src/tool_agent/tools.py` – Tool-Funktionen + JSON-Schemas (`TOOL_DEFINITIONS`, `TOOL_FUNCTIONS`)
- `src/tool_agent/agent.py` – Anthropic-Loop; `agent_openai.py` – OpenAI-Loop
- `src/tool_agent/common.py` – gemeinsamer Prompt, Schrittlimit und Fehler
- `src/tool_agent/api.py` – FastAPI-Endpoints

## Regeln
- Neues Tool = Funktion + Eintrag in `TOOL_DEFINITIONS` + `TOOL_FUNCTIONS` + Test in `tests/test_tools.py`.
- Tests dürfen keine echten API-Calls machen (Fake-Client wie in `tests/test_agent.py`).
- Keine Secrets im Code; Konfiguration über Umgebungsvariablen.
- Vor jedem Commit: Tests und Lint grün.
