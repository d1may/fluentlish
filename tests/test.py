import pytest
import requests
from bs4 import BeautifulSoup
from bot.services.parser_cambridge import get_cambridge_data  # Замените на имя вашего модуля

def test_get_cambridge_data_success():
    """Тест: успешное получение данных с Cambridge Dictionary."""
    result = get_cambridge_data("test")
    assert result is not None
    assert result["word"] == "test"
    assert result["part_of_speech"] in ["noun", "verb"]  # Возможные части речи для "test"
    assert result["definition"] != ""
    assert isinstance(result["examples"], list)
    assert result["level"] in ["A1", "A2", "B1", "B2", "C1", "C2", "—"]
    assert result["ipa_uk"] != ""
    assert result["ipa_us"] != ""

def test_get_cambridge_data_no_entries():
    """Тест: несуществующее слово, ожидается None."""
    result = get_cambridge_data("nonexistentword12345")
    assert result is None

def test_get_cambridge_data_server_error(monkeypatch):
    """Тест: сервер возвращает ошибку (не 200)."""
    def mock_get(*args, **kwargs):
        response = requests.Response()
        response.status_code = 404
        return response

    monkeypatch.setattr(requests, "get", mock_get)
    result = get_cambridge_data("test")
    assert result == []

def test_get_cambridge_data_missing_elements():
    """Тест: слово с ограниченными данными (например, без примеров)."""
    result = get_cambridge_data("obscure")  # Слово, которое может иметь меньше данных
    assert result is not None
    assert result["word"] == "obscure"
    assert result["definition"] != ""
    assert isinstance(result["examples"], list)
    assert result["level"] in ["A1", "A2", "B1", "B2", "C1", "C2", "—"]
    assert result["part_of_speech"] != "—"

if __name__ == "__main__":
    pytest.main([__file__])