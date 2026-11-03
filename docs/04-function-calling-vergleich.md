# Function Calling am tatsächlichen Code verstehen

Die übertragbare Struktur lautet: **Modell entscheidet, Python führt aus, Modell
verarbeitet das Ergebnis.** Beide Anbieter transportieren dieselben Informationen
in unterschiedlichen Formaten. Das SDK führt unsere Python-Funktionen nicht selbst aus.

## Wo Du was findest

- `projects/01-tool-agent/src/tool_agent/tools.py`: unveränderte Funktionen, Schemas und `run_tool`.
- `src/tool_agent/agent.py` im Projekt: bestehender Anthropic-Loop inklusive Beta-Konfiguration.
- `src/tool_agent/agent_openai.py`: neuer Responses-Loop.
- `src/tool_agent/common.py`: identischer Prompt, gemeinsames Schrittlimit und `AgentError`.
- `src/tool_agent/api.py`: Anbieterwahl mit bisherigem Standard Anthropic.

## Die Protokolle nebeneinander

| Schritt | Anthropic, `agent.py` | OpenAI, `agent_openai.py` |
|---|---|---|
| SDK-Aufruf | `client.beta.messages.create(...)` | `client.responses.create(...)` |
| Systemanweisung | `system=SYSTEM_PROMPT` | `instructions=SYSTEM_PROMPT` |
| Verlauf | `messages` mit Rollen und Content-Blöcken | `input` mit Nachrichten und typisierten Items |
| Tool-Schema | `name`, `description`, `input_schema`, `strict` | `type="function"`, `name`, `description`, `parameters`, `strict` |
| Tool-Aufruf erkennen | `stop_reason == "tool_use"` | `response.output` nach `type == "function_call"` filtern |
| Argumente | `block.input` ist bereits ein Dictionary | `call.arguments` ist JSON-Text, erst `json.loads(...)` |
| Aufruf zuordnen | `block.id` an `tool_use_id` zurückgeben | `call.call_id` an `call_id` zurückgeben, nicht `call.id` |
| Ergebnisformat | `tool_result`-Block mit `content` und `is_error` | `function_call_output`-Item mit `output` als String |
| Ergebnis im Verlauf | alle Ergebnisse in einer `user`-Nachricht | je Aufruf ein eigenständiges Output-Item ohne `role` |
| Endantwort | Textblöcke aus `response.content` verbinden | `response.output_text`, wenn keine Function Calls mehr vorliegen |

`openai_tools()` übersetzt die vorhandenen Schemas, statt sie ein zweites Mal zu
pflegen. Die Parameter sind bereits strict-kompatibel: alle Properties stehen in
`required`, zusätzliche Properties sind ausgeschlossen. Die Deep Copy verhindert,
dass der Adapter die Anthropic-Schemas versehentlich verändert. Strict garantiert
keine sinnvolle Rechnung oder gültige Zeitzone; dafür bleibt die lokale Fehlerbehandlung nötig.

## Beispiel: 6 × 7

Anthropic liefert sinngemäss einen Content-Block:

```json
{"type":"tool_use","id":"t1","name":"calculate","input":{"expression":"6*7"}}
```

`agent.py` führt `run_tool("calculate", {"expression": "6*7"})` aus. Danach
stehen die komplette Assistant-Antwort und folgende User-Nachricht im Verlauf:

```json
{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":"42","is_error":false}]}
```

OpenAI liefert stattdessen ein Output-Item:

```json
{"type":"function_call","id":"fc_1","call_id":"call_1","name":"calculate","arguments":"{\"expression\":\"6*7\"}"}
```

Nach dem Dekodieren läuft **dieselbe** Python-Funktion. Zurück geht:

```json
{"type":"function_call_output","call_id":"call_1","output":"{\"result\":\"42\",\"is_error\":false}"}
```

Das JSON **innerhalb** von `output` ist unsere eigene Vereinbarung, keine Vorgabe
von OpenAI. Die Responses API hat hier kein eigenes `is_error`-Feld. Wir machen den
Fehlerstatus deshalb im Inhalt ausdrücklich sichtbar. `tools_used` bleibt bei beiden
Varianten gleich und enthält den unverpackten Ergebnistext.

## Warum der vollständige Verlauf zählt

In beiden Loops wird die ursprüngliche Frage pro `ask()` neu angelegt. Eine
HTTP-Anfrage teilt daher kein Gespräch mit einer späteren HTTP-Anfrage.
Innerhalb des Loops gehen jedoch alle bisherigen Schritte erneut an das Modell.

Anthropic hängt `response.content` als Assistant-Nachricht an. OpenAI verwendet
`history.extend(response.output)`: Calls, Textnachrichten und Reasoning-Items bleiben
in ihrer Reihenfolge erhalten. Nur `output_text` zu speichern würde die Tool-Aufrufe
und gegebenenfalls Reasoning-Kontext verlieren. Mehrere Calls in einer Antwort
bekommen jeweils ein Ergebnis, bevor der nächste Modellaufruf erfolgt. Unsere
Python-Ausführung ist dabei sequenziell, auch wenn das Modell mehrere Calls liefert.

Der OpenAI-Loop verwendet `store=False` und lokalen Verlauf statt
`previous_response_id`. `include=["reasoning.encrypted_content"]` fordert die für
stateless Replay verwendbaren verschlüsselten Reasoning-Inhalte an. Aktuelle APIs
können diese bereits standardmässig liefern; das Include bleibt kompatibel.
`instructions` wird in jeder Runde erneut gesetzt. Dies ist keine Aussage über
sämtliche Datenaufbewahrungsregeln des Anbieters.

## Fehler und Abbruch

- `run_tool` liefert bei unbekannten Tools oder Ausführungsfehlern `(Text, True)`.
  Beide Loops geben das an das Modell zurück, damit es korrigieren kann.
- OpenAI-Argumente werden vor Ausführung als JSON-Objekt geprüft. Ungültiges JSON
  oder etwa `[]` wird mit derselben `call_id` als Fehler zurückgegeben.
- Bei OpenAI gilt nur `status == "completed"` als ausführbare Antwort.
  Unvollständige oder fehlgeschlagene Antworten werden vor der Tool-Ausführung abgelehnt.
  Refusal-Blöcke und leere Endantworten erzeugen ebenfalls `AgentError`.
- Anthropic behält seine bisherige Behandlung von `refusal` und `max_tokens`.
- Beide Loops begrenzen Modellrunden auf zehn. Das ist kein Limit der Anzahl von
  Tools in einer Runde und kein Geldlimit. SDK-Transportfehler bleiben SDK-Exceptions.

## Was die Tests beweisen und was noch offen bleibt

`tests/test_provider_comparison.py` lässt dieselben Rechnungs-, Wetter- und
Uhrzeitaufgaben durch beide Loops laufen. Geskriptete Modellantworten machen die
Tests reproduzierbar; die Uhr ist eingefroren. `tests/test_agent_openai.py` verwendet
echte SDK-Response-Typen und prüft den Verlauf, verschiedene IDs, mehrere Runden
sowie Fehler. `tests/conftest.py` blockiert Netzwerkzugriffe für die ganze Suite.

Das beweist, dass der lokale Agent die vorgegebenen Antworten korrekt verarbeitet.
Es beweist nicht, dass zwei echte Modelle dieselben Tools wählen oder gleich gute
Antworten liefern. Für die Anbieterwahl sind anschliessend echte, identische
Aufgaben mit expliziten Modellnamen, mehreren Wiederholungen und Messungen von
korrekten Ergebnissen, Kosten und Laufzeit nötig. Anthropic verwendet hier zudem
einen bestehenden serverseitigen Fallback, OpenAI keinen solchen Fallback. Das
muss bei einem späteren Modellvergleich berücksichtigt werden.

## Offizielle Referenzen

- [OpenAI: Function Calling mit der Responses API](https://developers.openai.com/api/docs/guides/function-calling)
- [OpenAI: API-Referenz und Reasoning-Verlauf](https://developers.openai.com/api/reference/overview)

Geprüft am 21. Oktober 2026. Die Erläuterung zu Anthropic beschreibt den vorhandenen
Projektcode; dessen Beta-Fallback wurde im Rahmen dieser Erweiterung nicht live getestet.
