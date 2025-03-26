import argparse
import pytest
from get_reports.create_review_document import _parse_arguments
import json
from get_reports.create_review_document import _load_observations
from get_reports.create_review_document import _create_document
from docx.document import Document


def test_parse_arguments_defaults(monkeypatch):
    """Test _parse_arguments with default arguments."""
    monkeypatch.setattr("sys.argv", ["create_review_document"])
    args = _parse_arguments()
    assert args.review_records_file == "reports/records_to_review.json"
    assert args.output_file == "reports/records_to_review.docx"
    assert args.verbose is False


def test_parse_arguments_custom_arguments(monkeypatch):
    """Test _parse_arguments with custom arguments."""
    monkeypatch.setattr(
        "sys.argv",
        [
            "create_review_document",
            "--review_records_file",
            "custom_records.json",
            "--output_file",
            "custom_output.docx",
            "--verbose",
        ],
    )
    args = _parse_arguments()
    assert args.review_records_file == "custom_records.json"
    assert args.output_file == "custom_output.docx"
    assert args.verbose is True


def test_parse_arguments_missing_required(monkeypatch):
    """Test _parse_arguments with missing required arguments."""
    monkeypatch.setattr("sys.argv", ["create_review_document"])
    try:
        args = _parse_arguments()
    except SystemExit as e:
        assert e.code == 0  # argparse exits with code 0 for help



def test_load_observations_valid_file(tmp_path):
    """Test _load_observations with a valid JSON file."""
    test_data = {"key": "value"}
    file_path = tmp_path / "test.json"
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(test_data, file)

    result = _load_observations(str(file_path))
    assert result == test_data


def test_load_observations_invalid_json(tmp_path):
    """Test _load_observations with an invalid JSON file."""
    file_path = tmp_path / "test.json"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("{invalid json}")

    with pytest.raises(json.JSONDecodeError):
        _load_observations(str(file_path))


def test_load_observations_file_not_found():
    """Test _load_observations with a non-existent file."""
    with pytest.raises(FileNotFoundError):
        _load_observations("non_existent_file.json")

