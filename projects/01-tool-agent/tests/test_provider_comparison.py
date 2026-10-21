"""Dieselben Aufgaben und dieselben echten Tools für beide Loops."""

from types import SimpleNamespace as NS

import pytest
from pydantic import ValidationError
from test_agent import FakeClient as AnthropicFake
from test_agent import text, tool_use
from test_agent_openai import FakeClient as OpenAIFake
from test_agent_openai import call, message, response

from tool_agent import agent, agent_openai, api
from tool_agent.common import AgentError


@pytest.mark.parametrize(
    "name, arguments, expected",
    [
        ("calculate", {"expression": "17*23"}, "391"),
        ("get_weather", {"city": "Berlin"}, "12 °C, bewölkt"),
        ("get_current_time", {"timezone": "Asia/Tokyo"}, "2026-10-21 16:00:00 JST"),
    ],
)
def test_same_task_and_tool_results(name, arguments, expected, monkeypatch):
    import json

    from tool_agent import tools

    class FixedDatetime:
        @staticmethod
        def now(zone):
            assert str(zone) == "Asia/Tokyo"
            return NS(strftime=lambda pattern: expected)

    monkeypatch.setattr(tools, "datetime", FixedDatetime)
    anthropic = AnthropicFake(
        [
            NS(stop_reason="tool_use", content=[tool_use("t1", name, arguments)]),
            NS(stop_reason="end_turn", content=[text(expected)]),
        ]
    )
    openai = OpenAIFake(
        [
            response(call(name=name, arguments=json.dumps(arguments))),
            response(message(expected)),
        ]
    )
    question = f"Nutze {name} mit {arguments}"
    assert (
        agent.ask(question, anthropic)
        == agent_openai.ask(question, openai)
        == {
            "answer": expected,
            "tools_used": [{"name": name, "input": arguments, "result": expected}],
        }
    )


@pytest.mark.parametrize("provider", ["anthropic", "openai"])
def test_api_dispatch(provider, monkeypatch):
    expected = {"answer": "42", "tools_used": []}

    def selected(question):
        assert question == "6*7?"
        return expected

    def wrong(question):
        pytest.fail("Falscher Anbieter gewählt")

    monkeypatch.setattr(api, "ask", selected if provider == "anthropic" else wrong)
    monkeypatch.setattr(api, "ask_openai", selected if provider == "openai" else wrong)
    assert api.ask_endpoint(api.Question(question="6*7?", provider=provider)) == expected


def test_api_default_validation_and_errors(monkeypatch):
    assert api.Question(question="Hi").provider == "anthropic"
    with pytest.raises(ValidationError):
        api.Question(question="Hi", provider="unknown")

    def fail(question):
        raise AgentError("Testfehler")

    monkeypatch.setattr(api, "ask_openai", fail)
    with pytest.raises(api.HTTPException) as exc:
        api.ask_endpoint(api.Question(question="Hi", provider="openai"))
    assert exc.value.status_code == 502
    assert exc.value.detail == "Testfehler"
