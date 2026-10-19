# 03 – Projekte strukturiert bauen

Der größte Unterschied zwischen „mit KI rumprobieren“ und „AI Engineering“ ist
ein fester Ablauf. Dieser hier funktioniert für jedes Projekt.

## Der 6-Schritte-Workflow

### 1. Problem in einem Satz
> „Nutzer schickt eine Frage, die App beantwortet sie und nutzt dafür bei Bedarf einen Rechner und eine Wetter-Funktion.“

Wenn du es nicht in einem Satz sagen kannst, ist das Projekt zu groß → aufteilen.

### 2. Einfachste Lösung wählen

| Stufe | Wann | Beispiel |
|-------|------|----------|
| **Ein LLM-Call** | Klassifizieren, Zusammenfassen, Extrahieren | E-Mail → Kategorie |
| **Workflow** (dein Code steuert, LLM in Schritten) | Ablauf ist bekannt | Text → Extrahieren → Validieren → Speichern |
| **Agent** (LLM entscheidet, welche Tools wann) | Ablauf ist offen | „Recherchiere und beantworte“ |

Starte immer eine Stufe niedriger, als du denkst.

### 3. Schnittstellen zuerst
Lege fest, *bevor* du Code schreibst:
- Eingabe/Ausgabe der API (z. B. `POST /ask {"question": str}` → `{"answer": str}`)
- Welche Tools gibt es, welche Parameter haben sie?

Schreib das in die `README.md`. Das ist auch der beste Prompt für Claude Code.

### 4. In kleinen Schritten bauen (mit Claude Code)

```
Plan Mode → Plan lesen/anpassen → umsetzen lassen → Tests laufen → verstehen → commit
```

Gute Prompts sind konkret:
- ❌ „Bau mir einen Agenten.“
- ✅ „Füge in `tools.py` ein Tool `convert_currency(amount, from, to)` hinzu, mit
  festen Kursen als Dictionary. Schreib Tests in `tests/test_tools.py`. Ändere sonst nichts.“

### 5. Testen – zwei Ebenen
- **Normale Tests** für deinen Code (Tools, Parsing, API) – laufen ohne API-Key, schnell, kostenlos.
- **Evals** für das Modellverhalten: eine Liste von Beispiel-Eingaben + erwartetes
  Verhalten, die du nach jeder Prompt-Änderung durchlaufen lässt.

### 6. Abschließen
- README aktualisieren (Wie starten? Was gelernt?)
- Commit + Push. Jedes Projekt ist ein Stück Portfolio.

## Git-Routine

```bash
git checkout -b feature/waehrungs-tool   # pro Feature ein Branch
# ... arbeiten ...
uv run pytest && uv run ruff check .
git add -p                                # Änderungen bewusst ansehen!
git commit -m "Währungsumrechnung als Tool hinzugefügt"
git push -u origin feature/waehrungs-tool
```

## Projekt-Ideen in steigender Schwierigkeit

| # | Projekt | Lernst du |
|---|---------|-----------|
| 01 | **Tool-Agent API** (in diesem Repo) | API-Calls, Function Calling, Agent-Loop, FastAPI |
| 02 | **Extraktions-Service**: Rechnungstext → JSON (Betrag, Datum, Firma) | Strukturierte Ausgaben, Validierung mit Pydantic, Evals |
| 03 | **Simulation**: zwei Agenten verhandeln (Käufer/Verkäufer) über N Runden, Ergebnis wird geloggt | Mehrere Prompts/Rollen, Zustand, Logging, Kosten im Blick |
| 04 | **Dokumenten-Chat**: Fragen zu eigenen PDFs | Dateien/PDF-Input, Kontext-Management, Zitate |
| 05 | **Deployment**: eins der Projekte als Web-App online (z. B. Railway, Fly.io, Render) | Docker, Umgebungsvariablen, Monitoring |

## Typische Anfängerfehler

- API-Key im Code committet → sofort im Dashboard widerrufen.
- Riesiger Prompt „mach alles“ statt kleiner Schritte.
- Kein Test für Tools → Agent ruft kaputte Funktion auf, du suchst den Fehler beim Modell.
- `stop_reason` ignorieren (z. B. `max_tokens` = Antwort abgeschnitten, `refusal` = abgelehnt).
- Frameworks zu früh: erst das rohe SDK verstehen.
