# Agentin-Exploration – Dein AI-Engineering-Setup

Ein strukturierter Lernpfad für den Einstieg ins AI Engineering: Apps, Funktionen
(Function Calling / Tools), Simulationen und APIs mit Large Language Models bauen.

## Aufbau des Repos

```
.
├── README.md                    ← du bist hier
├── docs/
│   ├── 00-my-setup.md           ← START HERE: my decided setup (Mac mini + iPad, Python)
│   ├── 01-tools-vergleich.md    ← Claude Code vs. OpenAI Codex & Co.
│   ├── 02-setup.md              ← Dein Arbeitsplatz Schritt für Schritt
│   └── 03-projekt-workflow.md   ← Wie du JEDES Projekt strukturiert baust
└── projects/
    └── 01-tool-agent/           ← Erstes Projekt: API + Agent mit Function Calling
```

## Lernpfad (empfohlene Reihenfolge)

| Woche | Ziel | Projekt |
|------|------|---------|
| 1 | Setup steht, erster API-Call | `docs/02-setup.md` durcharbeiten |
| 2 | Function Calling verstehen | `projects/01-tool-agent` lesen, laufen lassen, Tool hinzufügen |
| 3 | Eigene API bauen | Projekt 01 um einen eigenen Endpoint erweitern |
| 4 | Strukturierte Ausgaben + Tests | Projekt 02: Extraktions-Service (Text → JSON) |
| 5–6 | Simulation | Projekt 03: Multi-Agent-Simulation (z. B. Verhandlung zweier Agenten) |
| 7–8 | Deployment + Evals | Projekt 04: Eins deiner Projekte deployen und mit Tests/Evals absichern |

Ideen für die Projekte 02–04 stehen in [`docs/03-projekt-workflow.md`](docs/03-projekt-workflow.md#projekt-ideen-in-steigender-schwierigkeit).

## Die drei wichtigsten Regeln

1. **Verstehe, was die KI schreibt.** Lass dir Code erklären, bevor du ihn committest.
2. **Kleine Schritte, oft committen.** Eine Änderung → testen → commit.
3. **Erst simpel, dann komplex.** Ein einzelner API-Call löst mehr Probleme als du denkst. Agenten erst, wenn nötig.
