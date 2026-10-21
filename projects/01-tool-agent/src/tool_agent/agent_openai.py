"""OpenAI Responses API: derselbe Agent mit explizit verwaltetem Verlauf."""

import json
import os
from copy import deepcopy

from openai import OpenAI

from tool_agent.common import MAX_STEPS, SYSTEM_PROMPT, AgentError
from tool_agent.tools import TOOL_DEFINITIONS, run_tool

DEFAULT_MODEL = "gpt-5.4"


def openai_tools() -> list[dict]:
    """Nur das API-Format ändern; Schemas und Tool-Logik bleiben identisch."""
    return [
        {
            "type": "function",
            "name": tool["name"],
            "description": tool["description"],
            "parameters": deepcopy(tool["input_schema"]),
            "strict": tool["strict"],
        }
        for tool in TOOL_DEFINITIONS
    ]


def ask(question: str, client: OpenAI | None = None) -> dict:
    """Gleicher Rückgabevertrag wie agent.ask; Fake-Client für Offline-Tests."""
    client = client if client is not None else OpenAI()  # OPENAI_API_KEY
    model = os.environ.get("OPENAI_MODEL", DEFAULT_MODEL)
    history = [{"role": "user", "content": question}]
    tools_used = []

    for _ in range(MAX_STEPS):
        response = client.responses.create(
            model=model,
            instructions=SYSTEM_PROMPT,
            tools=openai_tools(),
            input=list(history),
            max_output_tokens=16000,
            store=False,
            # Für stateless Replay auch mit Reasoning-Modellen kompatibel.
            include=["reasoning.encrypted_content"],
        )
        # Keine unvollständigen Aufrufe ausführen oder Teilantwort als Erfolg melden.
        if response.status != "completed":
            raise AgentError(f"OpenAI-Antwort nicht abgeschlossen: {response.status}.")
        if any(
            part.type == "refusal"
            for item in response.output
            if item.type == "message"
            for part in item.content
        ):
            raise AgentError("Das Modell hat die Anfrage abgelehnt.")

        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            if not response.output_text:
                raise AgentError("OpenAI hat weder eine Textantwort noch Tool-Aufrufe geliefert.")
            return {"answer": response.output_text, "tools_used": tools_used}

        # Alle Items erhalten, auch Text und Reasoning, nicht nur Function Calls.
        history.extend(response.output)
        for call in calls:
            try:
                tool_input = json.loads(call.arguments)
                if not isinstance(tool_input, dict):
                    raise TypeError("Tool-Argumente müssen ein JSON-Objekt sein.")
            except (json.JSONDecodeError, TypeError) as exc:
                # Fehler mit derselben call_id zurückgeben: das Modell kann korrigieren.
                tool_input = {"invalid_arguments": call.arguments}
                result, is_error = f"Ungültige Tool-Argumente: {exc}", True
            else:
                result, is_error = run_tool(call.name, tool_input)
            tools_used.append({"name": call.name, "input": tool_input, "result": result})
            history.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,  # nicht call.id (ID des Output-Items)!
                    "output": json.dumps({"result": result, "is_error": is_error}, ensure_ascii=False),
                }
            )

    raise AgentError(f"Keine Antwort nach {MAX_STEPS} Schritten.")


if __name__ == "__main__":
    import sys

    frage = " ".join(sys.argv[1:]) or "Wie spät ist es in Tokio und was ist 17 * 23?"
    ergebnis = ask(frage)
    for tool in ergebnis["tools_used"]:
        print(f"[Tool] {tool['name']}({tool['input']}) -> {tool['result']}")
    print(ergebnis["answer"])
