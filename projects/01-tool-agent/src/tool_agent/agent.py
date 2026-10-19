"""Der Agent-Loop: das Herzstück jeder Function-Calling-App.

Ablauf:
  1. Frage + Tool-Beschreibungen ans Modell schicken
  2. Will das Modell ein Tool nutzen (stop_reason == "tool_use")?
     → Tool ausführen, Ergebnis zurückschicken, zurück zu 1.
  3. Sonst: fertige Antwort zurückgeben.

Alle Modell-Aufrufe passieren NUR in dieser Datei. Willst du später den Anbieter
wechseln (z. B. OpenAI), musst du nur hier etwas ändern.
"""

import os

import anthropic

from tool_agent.tools import TOOL_DEFINITIONS, run_tool

DEFAULT_MODEL = "claude-opus-5-5"
MAX_STEPS = 10  # Schutz gegen Endlosschleifen (und hohe Kosten)

SYSTEM_PROMPT = (
    "Du bist ein hilfsbereiter Assistent. Antworte auf Deutsch und knapp. "
    "Nutze die verfügbaren Tools für Rechnungen, Uhrzeiten und Wetter, "
    "statt Werte zu raten."
)


class AgentError(RuntimeError):
    """Der Agent konnte keine Antwort liefern."""


def ask(question: str, client: anthropic.Anthropic | None = None) -> dict:
    """Beantwortet eine Frage und gibt Antwort + benutzte Tools zurück."""
    client = client or anthropic.Anthropic()  # liest ANTHROPIC_API_KEY aus der Umgebung
    model = os.environ.get("MODEL", DEFAULT_MODEL)
    messages = [{"role": "user", "content": question}]
    tools_used = []

    for _ in range(MAX_STEPS):
        response = client.beta.messages.create(
            model=model,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
            # Lehnt das Modell eine Anfrage aus Sicherheitsgründen ab, versucht
            # die API es automatisch mit einem passenden anderen Modell.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )

        if response.stop_reason == "refusal":
            raise AgentError("Das Modell hat die Anfrage abgelehnt.")
        if response.stop_reason == "max_tokens":
            raise AgentError("Antwort wurde abgeschnitten (max_tokens erreicht).")

        if response.stop_reason != "tool_use":
            answer = "".join(b.text for b in response.content if b.type == "text")
            return {"answer": answer, "tools_used": tools_used}

        # Die komplette Antwort (inkl. tool_use-Blöcken) muss in den Verlauf.
        messages.append({"role": "assistant", "content": response.content})

        # Alle Tool-Ergebnisse gehören in EINE user-Nachricht.
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            result, is_error = run_tool(block.name, block.input)
            tools_used.append({"name": block.name, "input": block.input, "result": result})
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                    "is_error": is_error,
                }
            )
        messages.append({"role": "user", "content": tool_results})

    raise AgentError(f"Keine Antwort nach {MAX_STEPS} Schritten.")


if __name__ == "__main__":
    import sys

    frage = " ".join(sys.argv[1:]) or "Wie spät ist es in Tokio und was ist 17 * 23?"
    ergebnis = ask(frage)
    for tool in ergebnis["tools_used"]:
        print(f"[Tool] {tool['name']}({tool['input']}) -> {tool['result']}")
    print(ergebnis["answer"])
