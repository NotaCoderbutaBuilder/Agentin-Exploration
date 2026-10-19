"""HTTP-API rund um den Agenten. Start: uv run uvicorn tool_agent.api:app --reload"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from tool_agent.agent import AgentError, ask

app = FastAPI(title="Tool Agent")


class Question(BaseModel):
    question: str


class ToolCall(BaseModel):
    name: str
    input: dict
    result: str


class Answer(BaseModel):
    answer: str
    tools_used: list[ToolCall]


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ask", response_model=Answer)
def ask_endpoint(body: Question) -> dict:
    try:
        return ask(body.question)
    except AgentError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
