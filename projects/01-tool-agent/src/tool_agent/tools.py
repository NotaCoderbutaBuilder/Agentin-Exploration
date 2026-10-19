"""Die Funktionen, die das Modell aufrufen darf ("Tools" / Function Calling).

Jedes Tool besteht aus zwei Teilen:
1. einer normalen Python-Funktion (die Logik)
2. einer Beschreibung als JSON Schema (damit das Modell weiß, wann und wie es sie nutzt)
"""

import ast
import operator
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# --- 1. Die Funktionen ------------------------------------------------------

_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def calculate(expression: str) -> str:
    """Rechnet einen mathematischen Ausdruck sicher aus (kein eval()!)."""

    def _eval(node: ast.AST) -> float:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
            return _OPERATORS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
            return _OPERATORS[type(node.op)](_eval(node.operand))
        raise ValueError(f"Nicht erlaubter Ausdruck: {ast.dump(node)}")

    tree = ast.parse(expression, mode="eval")
    return str(_eval(tree.body))


def get_current_time(timezone: str = "Europe/Berlin") -> str:
    """Gibt die aktuelle Uhrzeit in einer Zeitzone zurück."""
    try:
        now = datetime.now(ZoneInfo(timezone))
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Unbekannte Zeitzone: {timezone}") from exc
    return now.strftime("%Y-%m-%d %H:%M:%S %Z")


# Absichtlich Fake-Daten: Übung für dich → ersetze das durch eine echte Wetter-API.
_FAKE_WEATHER = {
    "berlin": "12 °C, bewölkt",
    "münchen": "9 °C, Regen",
    "hamburg": "11 °C, windig",
}


def get_weather(city: str) -> str:
    """Liefert (simuliertes) Wetter für eine Stadt."""
    return _FAKE_WEATHER.get(city.strip().lower(), f"Keine Wetterdaten für {city}")


# --- 2. Die Beschreibungen für das Modell -----------------------------------

TOOL_DEFINITIONS = [
    {
        "name": "calculate",
        "description": "Rechnet einen mathematischen Ausdruck exakt aus. "
        "Nutze das für jede Rechnung, statt im Kopf zu rechnen.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "z. B. '(17 * 3) / 4'"},
            },
            "required": ["expression"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "name": "get_current_time",
        "description": "Gibt Datum und Uhrzeit in einer IANA-Zeitzone zurück.",
        "input_schema": {
            "type": "object",
            "properties": {
                "timezone": {"type": "string", "description": "z. B. 'Europe/Berlin'"},
            },
            "required": ["timezone"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "name": "get_weather",
        "description": "Gibt das aktuelle Wetter für eine deutsche Stadt zurück.",
        "input_schema": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]

TOOL_FUNCTIONS = {
    "calculate": calculate,
    "get_current_time": get_current_time,
    "get_weather": get_weather,
}


def run_tool(name: str, tool_input: dict) -> tuple[str, bool]:
    """Führt ein Tool aus. Gibt (Ergebnis, ist_fehler) zurück.

    Fehler werden nicht geworfen, sondern ans Modell zurückgegeben –
    so kann es sich korrigieren (z. B. eine andere Zeitzone probieren).
    """
    func = TOOL_FUNCTIONS.get(name)
    if func is None:
        return f"Unbekanntes Tool: {name}", True
    try:
        return func(**tool_input), False
    except Exception as exc:  # noqa: BLE001 - jeder Fehler geht als Text ans Modell
        return f"Fehler: {exc}", True
