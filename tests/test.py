import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from bot.services.parser_cambridge import get_cambridge_data


@pytest.mark.asyncio
async def test_get_cambridge_data_success():
    result = await get_cambridge_data("test")
    assert result is not None
    assert result["word"] == "test"
    assert result["part_of_speech"] in ["noun", "verb", "adjective"]
    assert result["definition"] != ""
    assert isinstance(result["examples"], list)
    assert result["level"] in ["A1", "A2", "B1", "B2", "C1", "C2", "—"]
    assert result["ipa_uk"] != ""
    assert result["ipa_us"] != ""


@pytest.mark.asyncio
async def test_get_cambridge_data_no_entries():
    result = await get_cambridge_data("nonexistentword12345")
    assert result is None


@pytest.mark.asyncio
async def test_get_cambridge_data_server_error():
    mock_response = AsyncMock()
    mock_response.status = 404
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=False)

    mock_session = MagicMock()
    mock_session.get = MagicMock(return_value=mock_response)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with patch("aiohttp.ClientSession", return_value=mock_session):
        result = await get_cambridge_data("test")
    assert result is None


@pytest.mark.asyncio
async def test_get_cambridge_data_missing_elements():
    result = await get_cambridge_data("obscure")
    assert result is not None
    assert result["word"] == "obscure"
    assert result["definition"] != ""
    assert isinstance(result["examples"], list)
    assert result["level"] in ["A1", "A2", "B1", "B2", "C1", "C2", "—"]
    assert result["part_of_speech"] != "—"


if __name__ == "__main__":
    pytest.main([__file__])
