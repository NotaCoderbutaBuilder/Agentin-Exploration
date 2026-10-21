"""Gemeinsamer Prompt, Schrittlimit und Fehler für beide Anbieter."""

MAX_STEPS = 10  # Schutz gegen Endlosschleifen (und hohe Kosten)

SYSTEM_PROMPT = (
    "Du bist ein hilfsbereiter Assistent. Antworte auf Deutsch und knapp. "
    "Nutze die verfügbaren Tools für Rechnungen, Uhrzeiten und Wetter, "
    "statt Werte zu raten."
)


class AgentError(RuntimeError):
    """Der Agent konnte keine Antwort liefern."""
