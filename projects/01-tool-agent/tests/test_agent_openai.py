"""Echte SDK-Antworttypen, geskriptete Antworten, keine API-Schlüssel nötig."""

import json
from copy import deepcopy
from types import SimpleNamespace as NS

import pytest
from openai.types.responses import Response

from tool_agent import agent_openai
from tool_agent.agent_openai import ask, openai_tools
from tool_agent.common import SYSTEM_PROMPT, AgentError
from tool_agent.tools import TOOL_DEFINITIONS


def response(*output, status="completed"):
    return Response.model_validate(
        {
            "id": "resp_test",
            "created_at": 0,
            "model": "offline-model",
            "object": "response",
            "status": status,
            "output": list(output),
            "parallel_tool_calls": True,
            "tool_choice": "auto",
            "tools": [],
        }
    )


def message(text="Fertig.", refusal=False):
    part = (
        {"type": "refusal", "refusal": text}
        if refusal
        else {
            "type": "output_text",
            "text": text,
            "annotations": [],
        }
    )
    return {
        "type": "message",
        "id": "msg_test",
        "role": "assistant",
        "status": "completed",
        "content": [part],
    }


def call(call_id="call_1", name="calculate", arguments='{"expression":"6*7"}'):
    return {
        "type": "function_call",
        "id": "fc_" + call_id,
        "call_id": call_id,
        "name": name,
        "arguments": arguments,
        "status": "completed",
    }


class FakeClient:
    def __init__(self, responses):
        self._responses = iter(responses)
        self.requests = []
        self.responses = NS(create=self._create)

    def _create(self, **kwargs):
        self.requests.append(deepcopy(kwargs))
        return next(self._responses)


def outputs(request):
    return [
        item
        for item in request["input"]
        if isinstance(item, dict) and item.get("type") == "function_call_output"
    ]


def test_answer_without_tools_and_configuration(monkeypatch):
    monkeypatch.setenv("MODEL", "anthropic-model-must-not-leak")
    monkeypatch.setenv("OPENAI_MODEL", "chosen-openai-model")
    client = FakeClient([response(message("Hallo!"))])
    assert ask("Hi", client) == {"answer": "Hallo!", "tools_used": []}
    request = client.requests[0]
    assert request["model"] == "chosen-openai-model"
    assert request["instructions"] == SYSTEM_PROMPT
    assert request["input"] == [{"role": "user", "content": "Hi"}]
    assert request["store"] is False
    assert request["include"] == ["reasoning.encrypted_content"]


def test_tool_schemas_match_without_mutating_anthropic():
    before = deepcopy(TOOL_DEFINITIONS)
    tools = openai_tools()
    for original, converted in zip(TOOL_DEFINITIONS, tools, strict=True):
        assert converted == {
            "type": "function",
            "name": original["name"],
            "description": original["description"],
            "parameters": original["input_schema"],
            "strict": True,
        }
    tools[0]["parameters"]["required"].clear()
    assert TOOL_DEFINITIONS == before


def test_multiple_calls_and_reasoning_replayed_across_rounds():
    first = response(
        {"id": "rs_test", "type": "reasoning", "summary": [], "encrypted_content": "opaque"},
        message("Ich prüfe beides."),
        call(),
        call("call_2", "get_weather", '{"city":"Berlin"}'),
    )
    second = response(call("call_3", arguments='{"expression":"42+1"}'))
    client = FakeClient([first, second, response(message("43; Berlin: 12 °C, bewölkt"))])
    result = ask("Rechne und prüfe Berlin", client)
    assert [tool["result"] for tool in result["tools_used"]] == ["42", "12 °C, bewölkt", "43"]
    request = client.requests[1]
    assert request["input"][1:5] == first.output
    assert request["instructions"] == SYSTEM_PROMPT
    assert [item["call_id"] for item in outputs(request)] == ["call_1", "call_2"]
    assert json.loads(outputs(request)[0]["output"]) == {"result": "42", "is_error": False}
    assert len(client.requests[0]["input"]) == 1  # kein nachträglich mutierter Verlauf
    assert client.requests[2]["input"][: len(request["input"])] == request["input"]
    assert outputs(client.requests[2])[-1]["call_id"] == "call_3"


@pytest.mark.parametrize(
    "tool_call, fragment",
    [
        (call(arguments="broken-json"), "Ungültige Tool-Argumente"),
        (call(arguments="[]"), "JSON-Objekt"),
        (call(arguments="null"), "JSON-Objekt"),
        (call(name="missing", arguments="{}"), "Unbekanntes Tool"),
        (call(arguments="{}"), "Fehler:"),
        (call(arguments='{"expression":"1/0"}'), "Fehler:"),
        (call(name="get_current_time", arguments='{"timezone":"Mond/Krater"}'), "Unbekannte Zeitzone"),
    ],
)
def test_tool_errors_return_with_call_id_and_allow_recovery(tool_call, fragment):
    client = FakeClient([response(tool_call), response(message("Korrigiert."))])
    assert ask("...", client)["answer"] == "Korrigiert."
    output = outputs(client.requests[1])[0]
    assert output["call_id"] == tool_call["call_id"]
    payload = json.loads(output["output"])
    assert payload["is_error"] is True
    assert fragment in payload["result"]


@pytest.mark.parametrize("status", ["incomplete", "failed", "cancelled", "in_progress", "queued"])
def test_unfinished_response_does_not_execute_tools(status, monkeypatch):
    def fail(*args):
        pytest.fail("Unvollständige Antwort darf keine Tools ausführen")

    monkeypatch.setattr(agent_openai, "run_tool", fail)
    with pytest.raises(AgentError, match="nicht abgeschlossen"):
        ask("...", FakeClient([response(call(), status=status)]))


def test_refusal_and_empty_output():
    with pytest.raises(AgentError, match="abgelehnt"):
        ask("...", FakeClient([response(message("Nein.", refusal=True))]))
    with pytest.raises(AgentError, match="weder"):
        ask("...", FakeClient([response()]))


def test_step_limit(monkeypatch):
    monkeypatch.setattr(agent_openai, "MAX_STEPS", 2)
    client = FakeClient([response(call()), response(call("call_2"))])
    with pytest.raises(AgentError, match="2 Schritten"):
        ask("...", client)
    assert len(client.requests) == 2
