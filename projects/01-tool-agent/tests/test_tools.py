import pytest

from tool_agent.tools import calculate, get_weather, run_tool


def test_calculate_basic():
    assert calculate("17 * 23") == "391"
    assert calculate("(10 + 2) / 4") == "3.0"
    assert calculate("-2 ** 2") == "-4"


def test_calculate_rejects_code():
    with pytest.raises(ValueError):
        calculate("__import__('os').system('ls')")


def test_get_weather_is_case_insensitive():
    assert get_weather(" Berlin ") == "12 °C, bewölkt"
    assert "Keine Wetterdaten" in get_weather("Atlantis")


def test_run_tool_returns_errors_instead_of_raising():
    assert run_tool("gibt_es_nicht", {}) == ("Unbekanntes Tool: gibt_es_nicht", True)
    result, is_error = run_tool("get_current_time", {"timezone": "Mond/Krater"})
    assert is_error
    assert "Unbekannte Zeitzone" in result
