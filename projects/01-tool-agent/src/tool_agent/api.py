"""HTTP-API rund um den Agenten. Start: uv run uvicorn tool_agent.api:app --reload"""

from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from tool_agent.agent import ask
from tool_agent.agent_openai import ask as ask_openai
from tool_agent.common import AgentError

app = FastAPI(title="Tool Agent")


class Question(BaseModel):
    question: str
    provider: Literal["anthropic", "openai"] = "anthropic"


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
        agent = ask_openai if body.provider == "openai" else ask
        return agent(body.question)
    except AgentError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
