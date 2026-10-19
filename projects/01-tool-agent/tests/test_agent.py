"""Testet den Agent-Loop OHNE echten API-Call: ein Fake-Client spielt das Modell.

So sind Tests schnell, kostenlos und reproduzierbar.
"""

from types import SimpleNamespace as NS

import pytest

from tool_agent.agent import AgentError, ask


class FakeClient:
    """Gibt vorher festgelegte Antworten zurück und merkt sich die Anfragen."""

    def __init__(self, responses):
        self._responses = iter(responses)
        self.requests = []
        self.beta = NS(messages=NS(create=self._create))

    def _create(self, **kwargs):
        self.requests.append(kwargs)
        return next(self._responses)


def text(t):
    return NS(type="text", text=t)


def tool_use(id_, name, input_):
    return NS(type="tool_use", id=id_, name=name, input=input_)


def test_answer_without_tools():
    client = FakeClient([NS(stop_reason="end_turn", content=[text("Hallo!")])])
    assert ask("Hi", client=client) == {"answer": "Hallo!", "tools_used": []}


def test_tool_call_then_answer():
    client = FakeClient(
        [
            NS(stop_reason="tool_use", content=[tool_use("t1", "calculate", {"expression": "6*7"})]),
            NS(stop_reason="end_turn", content=[text("Das Ergebnis ist 42.")]),
        ]
    )
    result = ask("Was ist 6*7?", client=client)

    assert result["answer"] == "Das Ergebnis ist 42."
    assert result["tools_used"] == [{"name": "calculate", "input": {"expression": "6*7"}, "result": "42"}]
    # Das Tool-Ergebnis muss mit passender ID zurück ans Modell gehen.
    tool_result = client.requests[1]["messages"][-1]["content"][0]
    assert tool_result["tool_use_id"] == "t1"
    assert tool_result["content"] == "42"


def test_refusal_raises():
    client = FakeClient([NS(stop_reason="refusal", content=[])])
    with pytest.raises(AgentError):
        ask("...", client=client)
