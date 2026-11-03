# Projekt 01 – Tool Agent (Function Calling + API)

**In einem Satz:** Eine HTTP-API, die Fragen beantwortet und dafür selbst
entscheidet, ob sie einen Rechner, eine Uhr oder eine Wetter-Funktion aufruft.

## Was du hier lernst
- Wie ein LLM-API-Call aussieht (Anthropic Messages API und OpenAI Responses API, offizielle Python-SDKs)
- **Function Calling**: Tools definieren, ausführen, Ergebnisse zurückgeben
- Den **Agent-Loop** (`agent.py`) – in jedem Agenten-Framework steckt genau das
- Eine API mit **FastAPI** bauen
- Code testen, **ohne** für jeden Test die API zu bezahlen (Fake-Client)

## Starten

```bash
cd projects/01-tool-agent
cp .env.example .env          # API-Key eintragen
uv sync --locked              # reproduzierbare Abhängigkeiten installieren
uv run pytest                 # Tests (brauchen keinen API-Key)

set -a; source .env; set +a   # Key in die Shell laden
uv run python -m tool_agent.agent "Was ist 17 * 23 und wie ist das Wetter in Berlin?"
uv run python -m tool_agent.agent_openai "Was ist 17 * 23 und wie ist das Wetter in Berlin?"

uv run uvicorn tool_agent.api:app --reload
# dann im Browser: http://127.0.0.1:8000/docs  → /ask ausprobieren
```

## So fließen die Daten

```
Frage ─▶ Modell ──"tool_use: calculate(17*23)"──▶ run_tool() ─▶ "391"
           ▲                                                   │
           └──────────────── tool_result ◀─────────────────────┘
         Modell ─▶ "17 × 23 = 391. In Berlin sind es 12 °C ..." ─▶ Antwort
```

## Übungen (in dieser Reihenfolge)
1. **Lesen:** Geh `agent.py` Zeile für Zeile durch. Lass dir von Claude Code
   jede Zeile erklären, die du nicht verstehst.
2. **Neues Tool:** `convert_currency(amount, from_currency, to_currency)` mit festen Kursen.
   Regeln stehen in `CLAUDE.md`. Erst Plan Mode, dann umsetzen.
3. **Echte Daten:** Ersetze `get_weather` durch eine echte, kostenlose Wetter-API (z. B. Open-Meteo).
4. **Kosten sichtbar machen:** Gib `response.usage` (Input-/Output-Tokens) mit in der API-Antwort zurück.
5. **Vergleich:** Lies `agent.py` und `agent_openai.py` nebeneinander.
   Die Umsetzung ist vorhanden. Erkläre für jeden Schritt, welche API-Struktur sich ändert.

## Anbieter auswählen

Die bisherige CLI bleibt Anthropic. `agent_openai` verwendet OpenAI Responses,
kein Chat Completions und kein Agents-Framework. Nur der jeweilige API-Key ist nötig.
`MODEL` bleibt die Anthropic-Modellwahl; OpenAI liest separat `OPENAI_MODEL`
(Standard: `gpt-5.4`, bei Bedarf ein für Dein Konto verfügbares Modell wählen).

Die HTTP-API behält Anthropic als Standard. OpenAI wählst Du im Request:

```json
{"question": "Was ist 17 * 23 und wie ist das Wetter in Berlin?", "provider": "openai"}
```

Beide geben dieselbe Struktur zurück: `{"answer": "...", "tools_used": [...]}`.
Die Funktionen `calculate`, `get_current_time` und `get_weather` sind identisch.
Wetter bleibt eine lokale Simulation; die Uhrzeit ist beim echten Aufruf dynamisch.

## Offline reproduzieren

```bash
uv sync --locked
uv run --locked pytest -q
uv run --locked ruff check .
```

Nach einmaliger Installation funktionieren diese Befehle auch mit `uv run --offline --locked`.
Die Tests brauchen keine Schlüssel und blockieren Netzwerkverbindungen ausdrücklich.
OpenAI-Fakes liefern echte `openai.types.responses.Response`-Objekte. Geprüft werden
mehrere Calls in einer Antwort, Folgerunden, kompletter Verlauf inklusive Reasoning,
Call-IDs, Tool- und Argumentfehler, Ablehnung, unvollständige Antworten und Schrittlimit.
Ein gemeinsamer Vergleichstest lässt beide Loops dieselben Tools ausführen; die Uhr
wird darin festgesetzt. Das prüft Protokoll und lokale Logik, nicht Modellqualität,
Preis, Latenz oder die Verfügbarkeit eines Modells im eigenen Konto.

Der Ablauf und die konkreten Unterschiede stehen in
[docs/04-function-calling-vergleich.md](../../docs/04-function-calling-vergleich.md).
