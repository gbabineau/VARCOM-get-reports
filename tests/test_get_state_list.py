import json
import logging
from unittest.mock import mock_open, patch

import pytest

from get_reports.get_state_list import get_state_list


@pytest.fixture
def mock_taxonomy():
    return [
        {"comName": "American Robin"},
        {"comName": "Northern Cardinal"},
        {"comName": "Blue Jay"},
    ]


@pytest.fixture
def mock_state_list():
    return {
        "state_list": [
            {"comName": "American Robin"},
            {"comName": "Northern Cardinal"},
            {"comName": "Unknown Species"},
        ]
    }


def test_get_state_list_file_not_exist(caplog, mock_taxonomy):
    with caplog.at_level(logging.ERROR):
        result = get_state_list("non_existent_file.json", mock_taxonomy)
    assert result == {}
    assert "File non_existent_file.json does not exist." in caplog.text


def test_get_state_list_valid_file(caplog, mock_taxonomy, mock_state_list):
    mock_file_data = json.dumps(mock_state_list)
    with (
        patch("builtins.open", mock_open(read_data=mock_file_data)),
        patch("os.path.exists", return_value=True),
    ):
        with caplog.at_level(logging.INFO):
            result = get_state_list("valid_file.json", mock_taxonomy)
    assert result == mock_state_list["state_list"]
    assert (
        "Checking species in state list against eBird taxonomy." in caplog.text
    )


def test_get_state_list_species_not_in_taxonomy(
    caplog, mock_taxonomy, mock_state_list
):
    mock_file_data = json.dumps(mock_state_list)
    with (
        patch("builtins.open", mock_open(read_data=mock_file_data)),
        patch("os.path.exists", return_value=True),
    ):
        with caplog.at_level(logging.WARNING):
            result = get_state_list("valid_file.json", mock_taxonomy)
    assert result == mock_state_list["state_list"]
    assert "Species Unknown Species not found in eBird taxonomy" in caplog.text
