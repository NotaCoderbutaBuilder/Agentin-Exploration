# Projekt 01 – Tool Agent (Function Calling + API)

**In einem Satz:** Eine HTTP-API, die Fragen beantwortet und dafür selbst
entscheidet, ob sie einen Rechner, eine Uhr oder eine Wetter-Funktion aufruft.

## Was du hier lernst
- Wie ein LLM-API-Call aussieht (Claude Messages API, offizielles Python-SDK)
- **Function Calling**: Tools definieren, ausführen, Ergebnisse zurückgeben
- Den **Agent-Loop** (`agent.py`) – in jedem Agenten-Framework steckt genau das
- Eine API mit **FastAPI** bauen
- Code testen, **ohne** für jeden Test die API zu bezahlen (Fake-Client)

## Starten

```bash
cd projects/01-tool-agent
cp .env.example .env          # API-Key eintragen
uv sync                       # Abhängigkeiten installieren
uv run pytest                 # Tests (brauchen keinen API-Key)

set -a; source .env; set +a   # Key in die Shell laden
uv run python -m tool_agent.agent "Was ist 17 * 23 und wie ist das Wetter in Berlin?"

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
5. **Vergleich:** Baue `agent.py` als `agent_openai.py` mit dem OpenAI-SDK nach. Was ist gleich, was anders?
