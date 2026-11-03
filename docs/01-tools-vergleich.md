# 01 – Tools im Vergleich: Claude Code, OpenAI & Co.

Zuerst eine wichtige Unterscheidung, die Anfänger oft durcheinanderbringen:

| Kategorie | Wofür? | Beispiele |
|-----------|--------|-----------|
| **Coding-Agent** (hilft *dir* beim Programmieren) | Code schreiben, refactoren, debuggen, Tests laufen lassen | Claude Code, OpenAI Codex, Cursor, GitHub Copilot, Gemini CLI |
| **Model-API** (die KI *in deiner App*) | Deine App ruft ein Modell auf, z. B. Chatbot, Extraktion, Agent | Anthropic Claude API, OpenAI API, Google Gemini API |
| **Agent-Frameworks / SDKs** | Agenten-Loop, Tools, Gedächtnis in deiner App | Claude Agent SDK, OpenAI Agents SDK, LangGraph |

Du brauchst als AI Engineer **beides**: ein Werkzeug, das dir beim Bauen hilft,
und eine API, die deine App antreibt. Die beiden müssen nicht vom selben Anbieter sein.

---

## Claude Code (Anthropic)

Ein agentisches Coding-Tool, das im Terminal, in VS Code/JetBrains, als Desktop-App
und im Web läuft. Es liest dein Repo, führt Befehle aus, bearbeitet Dateien und
committet – du gibst Ziele vor, es arbeitet die Schritte ab.

**Vorteile**

- **Arbeitet im ganzen Projekt, nicht nur in einer Datei.** Es sucht selbst nach
  relevantem Code, führt Tests aus und iteriert, bis sie grün sind.
- **`CLAUDE.md` = Projektgedächtnis.** Eine Datei im Repo mit Konventionen,
  Befehlen und Regeln. Wird bei jeder Session automatisch geladen. Ideal, um
  deinen eigenen Standard festzuschreiben (siehe `projects/01-tool-agent/CLAUDE.md`).
- **Plan Mode.** Claude plant erst und wartet auf deine Freigabe, bevor es Code
  ändert – perfekt zum Lernen, weil du den Plan verstehst, bevor etwas passiert.
- **Erweiterbar:**
  - *Slash Commands & Skills* – wiederverwendbare Arbeitsabläufe (z. B. `/code-review`).
  - *Hooks* – automatische Aktionen (z. B. „nach jeder Änderung Linter laufen lassen“).
  - *MCP-Server* – Anbindung an GitHub, Datenbanken, Browser, Docs usw.
  - *Subagents* – Teilaufgaben parallel an spezialisierte Helfer delegieren.
- **Berechtigungssystem.** Du entscheidest, was es ohne Nachfrage darf.
- **Cloud-Sessions.** Aufgaben im Web/Handy starten, Claude arbeitet in einem
  Container und pusht auf einen Branch (so ist dieses Repo entstanden).
- **Claude Agent SDK.** Derselbe Agent als Bibliothek – du kannst eigene Agenten
  auf derselben Basis bauen.

**Nachteile / worauf achten**

- Kostet Abo oder API-Tokens; lange Sessions können teuer werden.
- Gefahr, Code zu übernehmen, den du nicht verstehst → bewusst gegensteuern.

## OpenAI Codex (OpenAI)

OpenAIs Gegenstück: Codex CLI (Open Source, Terminal), IDE-Erweiterung und
Codex in der Cloud (Aufgaben parallel in Sandboxes, Ergebnis als PR).

**Vorteile**

- CLI ist Open Source – du kannst nachlesen, wie ein Coding-Agent funktioniert.
- Gute Integration in ChatGPT-Abos und GitHub.
- `AGENTS.md` als Projektanweisungsdatei (vergleichbar mit `CLAUDE.md`).

**OpenAI-Plattform für deine Apps**

- **Responses API** mit Function Calling, eingebauten Tools (Websuche, Dateisuche,
  Code Interpreter) und strukturierten Ausgaben.
- **Agents SDK** (Python/TS) für Multi-Agent-Setups mit Handoffs und Guardrails.
- Großes Ökosystem: Embeddings, Bild-, Audio- und Echtzeit-Sprach-APIs.

## Weitere Tools kurz

| Tool | Stärke |
|------|--------|
| **Cursor** | KI-first Editor (VS-Code-Fork), sehr gute Inline-Edits, kann mehrere Modelle nutzen |
| **GitHub Copilot** | Autocomplete + Agent-Modus direkt in GitHub/VS Code, gut im Team-Kontext |
| **Gemini CLI** | Googles Terminal-Agent, großzügiges Gratis-Kontingent |
| **Windsurf, Zed, Aider** | Alternativen mit eigenen Schwerpunkten (Aider: Open Source, Git-zentriert) |

## Claude API vs. OpenAI API (für deine Apps)

Die Konzepte sind fast identisch – wer eines versteht, versteht das andere:

| Konzept | Claude API | OpenAI API |
|---------|-----------|------------|
| Grund-Endpoint | `POST /v1/messages` | Responses API |
| Funktionen aufrufen | `tools` + `tool_use` / `tool_result` Blöcke | `tools` + Function Calls / Outputs |
| Strukturierte Ausgabe | `output_config.format` (JSON Schema) | `text.format` / Structured Outputs |
| „Nachdenken“ | Adaptive Thinking + `effort` | Reasoning-Modelle + `reasoning.effort` |
| Kosten sparen | Prompt Caching, Batch API (-50 %) | Prompt Caching, Batch API (-50 %) |
| Agent-SDK | Claude Agent SDK | OpenAI Agents SDK |

**Praxistipp:** Kapsle den LLM-Aufruf in deiner App in *einem* Modul
(siehe `projects/01-tool-agent/src/tool_agent/agent.py`). Dann ist ein
Anbieterwechsel später eine Änderung an einer Stelle statt im ganzen Code.

## Meine Empfehlung für dich

1. **Ein Coding-Agent als Hauptwerkzeug** – lerne ihn richtig (Plan Mode,
   `CLAUDE.md`, Hooks) statt fünf Tools oberflächlich. Claude Code ist dafür
   eine sehr gute Wahl, Codex ist eine gleichwertige Alternative zum Ausprobieren.
2. **Eine Model-API wirklich verstehen** – mit dem offiziellen SDK, ohne
   Frameworks. Frameworks (LangChain etc.) erst, wenn du merkst, dass du sie brauchst.
3. **Preise und Modelle ändern sich schnell.** Prüfe immer die offiziellen Docs:
   - Claude Code: https://code.claude.com/docs
   - Claude API: https://platform.claude.com/docs
   - OpenAI: https://platform.openai.com/docs

## Praktischer Vergleich im Repository

Projekt 01 enthält jetzt beide selbst implementierten Loops: `agent.py` für
Anthropic und `agent_openai.py` für OpenAI Responses. Sie teilen Tools, Prompt
und Rückgabeformat. Den Ablauf mit konkreten Request-/Response-Beispielen und den
Grenzen der Offline-Tests erklärt [04-function-calling-vergleich.md](04-function-calling-vergleich.md).
