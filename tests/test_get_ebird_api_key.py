import pytest

from get_reports.get_ebird_api_key import ebird_api_key_name, get_ebird_api_key


def test_get_ebird_api_key_valid(monkeypatch):
    # Set a valid API key in the environment variable
    monkeypatch.setenv(ebird_api_key_name, "valid_api_key")
    assert get_ebird_api_key() == "valid_api_key"


def test_get_ebird_api_key_missing(monkeypatch):
    # Unset the environment variable
    monkeypatch.delenv(ebird_api_key_name, raising=False)
    assert get_ebird_api_key() is None


def test_get_ebird_api_key_invalid(monkeypatch):
    # Set the environment variable to "0" to simulate an invalid key
    monkeypatch.setenv(ebird_api_key_name, "0")
    with pytest.raises(SystemExit) as exception_information:
        get_ebird_api_key()
    assert exception_information.type == SystemExit
    assert "ebird API key must be specified" in str(exception_information.value)
