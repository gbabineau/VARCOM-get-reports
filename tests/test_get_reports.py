import sys
from unittest.mock import MagicMock, mock_open, patch
import logging
import pytest

from get_reports.get_reports import (
    _parse_arguments,
    _save_records_to_file,
    main,
)


def test_parse_arguments_required_fields():
    test_args = ["get_reports", "--year", "2023", "--month", "10"]
    sys.argv = test_args
    args = _parse_arguments()
    assert args.year == 2023
    assert args.month == 10
    assert args.input == "get_reports/data/varcom_review_species.json"
    assert args.state == "US-VA"
    assert not args.verbose


def test_parse_arguments_optional_fields():
    test_args = [
        "get_reports",
        "--year",
        "2023",
        "--month",
        "10",
        "--input",
        "custom_species.json",
        "--state",
        "US-NY",
        "--verbose",
    ]
    sys.argv = test_args
    args = _parse_arguments()
    assert args.year == 2023
    assert args.month == 10
    assert args.input == "custom_species.json"
    assert args.state == "US-NY"
    assert args.verbose


def test_parse_arguments_missing_required_fields():
    test_args = ["get_reports", "--year", "2023"]
    sys.argv = test_args
    with pytest.raises(SystemExit):
        _parse_arguments()


def test_parse_arguments_version_flag():
    test_args = ["get_reports", "--version"]
    sys.argv = test_args
    with pytest.raises(SystemExit) as excinfo:
        _parse_arguments()
    assert excinfo.value.code == 0


@patch("get_reports.get_reports.datetime")
@patch("builtins.open", new_callable=mock_open)
def test_save_records_to_file(mock_open, mock_datetime):
    # Mock the current date
    mock_datetime.now.return_value.strftime.return_value = "2023-10-15"

    # Test data
    records = [{"species": "Cardinal", "location": "Park"}]
    year = 2023
    month = 10
    state = "US-VA"

    # Call the function
    _save_records_to_file(records, year, month, state)

    # Expected output
    expected_filename = "reports/records_to_review_2023_10.json"
    expected_data = {
        "date of observations": "2023,10",
        "state": "US-VA",
        "date of report": "2023-10-15",
        "records": records,
    }

    # Assert the file was opened with the correct filename and mode
    mock_open.assert_called_once_with(
        expected_filename, "wt", encoding="utf-8"
    )

    # Assert the correct data was written to the file
    handle = mock_open()
    assert handle.write.call_count == 32


@patch("builtins.open", new_callable=mock_open)
def test_save_records_to_file_no_records(mock_open):
    # Test data
    records = []
    year = 2023
    month = 10
    state = "US-VA"

    # Call the function
    _save_records_to_file(records, year, month, state)

    # Assert the file was not opened since there are no records
    mock_open.assert_not_called()


@patch("get_reports.get_reports._parse_arguments")
@patch("get_reports.get_reports.logging.basicConfig")
@patch("get_reports.get_reports.get_ebird_api_key.get_ebird_api_key")
@patch("get_reports.get_reports.get_taxonomy")
@patch("get_reports.get_reports.get_state_list.get_state_list")
@patch("get_reports.get_reports.get_regions")
@patch("get_reports.get_reports.get_review_rules.get_review_rules")
@patch("get_reports.get_reports.get_records_to_review.get_records_to_review")
@patch("get_reports.get_reports._save_records_to_file")
def test_main(
    mock_save_records_to_file,
    mock_get_records_to_review,
    mock_get_review_rules,
    mock_get_regions,
    mock_get_state_list,
    mock_get_taxonomy,
    mock_get_ebird_api_key,
    mock_logging,
    mock_parse_arguments,
):
    # Mock the parsed arguments
    mock_args = MagicMock()
    mock_args.year = 2023
    mock_args.month = 10
    mock_args.state = "US-VA"
    mock_args.input = "custom_species.json"
    mock_args.verbose = True
    mock_parse_arguments.return_value = mock_args

    # Mock the return values of the functions
    mock_get_ebird_api_key.return_value = "mock_api_key"
    mock_get_taxonomy.return_value = "mock_taxonomy"
    mock_get_state_list.return_value = ["mock_state_list"]
    mock_get_regions.return_value = ["mock_county"]
    mock_get_review_rules.return_value = ["mock_species"]
    mock_get_records_to_review.return_value = ["mock_record"]

    # Call the main function
    main()

    # Assertions
    mock_parse_arguments.assert_called_once()
    mock_logging.assert_called_once_with(level=logging.INFO)
    mock_get_ebird_api_key.assert_called_once()
    mock_get_taxonomy.assert_called_once_with("mock_api_key")
    mock_get_state_list.assert_called_once_with(
        "custom_species.json", taxonomy="mock_taxonomy"
    )
    mock_get_regions.assert_called_once_with(
        token="mock_api_key", rtype="subnational2", region="US-VA"
    )
    mock_get_review_rules.assert_called_once_with(
        "custom_species.json", "mock_taxonomy", ["mock_county"], "US-VA"
    )
    mock_get_records_to_review.assert_called_once_with(
        "mock_api_key",
        ["mock_state_list"],
        ["mock_county"],
        2023,
        10,
        ["mock_species"],
    )
    mock_save_records_to_file.assert_called_once_with(
        ["mock_record"], 2023, 10, "US-VA"
    )
