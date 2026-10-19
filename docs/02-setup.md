# 02 – Dein Setup Schritt für Schritt

Ziel: Ein Arbeitsplatz, auf dem du jedes neue AI-Projekt in 5 Minuten startest.

## 1. Basis-Werkzeuge

| Werkzeug | Warum | Installation |
|----------|-------|--------------|
| **Git** + GitHub-Account | Versionskontrolle, Backup, Portfolio | https://git-scm.com |
| **VS Code** (oder Cursor) | Editor | https://code.visualstudio.com |
| **Python 3.11+** | Hauptsprache für AI Engineering | über `uv` (siehe unten) |
| **uv** | Schneller Paket- und Projektmanager für Python | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Node.js LTS** (optional) | Für Web-Frontends / TypeScript | https://nodejs.org |
| **Claude Code** | Coding-Agent | siehe https://code.claude.com/docs (Installationsbefehl dort) |

> **Warum Python?** Fast alle AI-Bibliotheken, Beispiele und SDKs erscheinen zuerst
> für Python. TypeScript ist die gute zweite Sprache, sobald du Web-UIs baust.

## 2. API-Keys sicher verwalten

1. Key holen: https://platform.claude.com (Anthropic) bzw. https://platform.openai.com (OpenAI).
2. **Niemals** Keys in Code oder Git. Stattdessen:
   - lokal in einer `.env`-Datei (steht in `.gitignore`)
   - im Repo nur eine `.env.example` mit Platzhaltern
3. Ausgabenlimit (Spend Limit) im Dashboard setzen – schützt vor bösen Überraschungen.

## 3. Claude Code einrichten

```bash
cd mein-projekt
claude            # startet die Session im Projektordner
/init             # erzeugt eine CLAUDE.md aus deinem Code
```

Nützliche Gewohnheiten:

- **Shift+Tab** wechselt in den *Plan Mode* → erst Plan lesen, dann freigeben.
- `/clear` zwischen unabhängigen Aufgaben – frischer Kontext = bessere Ergebnisse.
- Bitte Claude, **Tests zu schreiben und auszuführen**, nicht nur Code.
- Lass dir unbekannte Konzepte erklären: *„Erklär mir Zeile 20–40, als wäre ich Junior.“*

## 4. Projekt-Template

Jedes Projekt bekommt dieselbe Struktur (Beispiel: `projects/01-tool-agent`):

```
mein-projekt/
├── CLAUDE.md          # Regeln & Befehle für den Coding-Agenten
├── README.md          # Was, warum, wie starten
├── pyproject.toml     # Abhängigkeiten & Tool-Konfiguration
├── .env.example       # Welche Umgebungsvariablen nötig sind
├── src/mein_paket/    # Der eigentliche Code
└── tests/             # Tests (pytest)
```

Neues Projekt anlegen:

```bash
uv init --package mein-projekt
cd mein-projekt
uv add anthropic fastapi uvicorn
uv add --dev pytest ruff
git init && git add . && git commit -m "Projekt-Grundgerüst"
```

## 5. Checkliste „Setup fertig“

- [ ] `git --version`, `uv --version`, `python --version` funktionieren
- [ ] Claude Code startet im Projektordner
- [ ] API-Key liegt in `.env`, Spend Limit gesetzt
- [ ] `projects/01-tool-agent` läuft (`uv run pytest` ist grün)
