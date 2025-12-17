"""Tests for the create_review_document module."""
import argparse
import json
import logging

import pytest

from get_reports.create_review_document import (
    _add_county_records,
    _add_document_header,
    _add_species_heading,
    _add_observation_data,
    _add_species_records,
    _create_document,
    _load_observations,
    _parse_arguments,
    _save_document,
    main,
)

LIST_BULLET_STYLE = "List Bullet"


def test_parse_arguments_defaults(monkeypatch):
    """Test _parse_arguments with default arguments."""
    monkeypatch.setattr("sys.argv", ["create_review_document"])
    args = _parse_arguments()
    assert args.input == "reports/records_to_review.json"
    assert args.output == "reports/records_to_review.docx"
    assert args.verbose is False


def test_parse_arguments_custom_arguments(monkeypatch):
    """Test _parse_arguments with custom arguments."""
    monkeypatch.setattr(
        "sys.argv",
        [
            "create_review_document",
            "--input",
            "custom_records.json",
            "--output",
            "custom_output.docx",
            "--verbose",
        ],
    )
    args = _parse_arguments()
    assert args.input == "custom_records.json"
    assert args.output == "custom_output.docx"
    assert args.verbose is True


def test_parse_arguments_missing_required(monkeypatch):
    """Test _parse_arguments with missing required arguments."""
    monkeypatch.setattr("sys.argv", ["create_review_document"])
    try:
        _parse_arguments()
    except SystemExit as e:
        assert e.code == 0  # argparse exits with code 0 for help


def test_load_observations_valid_file(tmp_path):
    """Test _load_observations with a valid JSON file."""
    test_data = {"key": "value"}
    file_path = tmp_path / "test.json"
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(test_data, indent=4, fp=file)

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


def test_create_document_valid_observations(mocker):
    """Test _create_document with valid observations."""
    mock_document = mocker.patch("get_reports.create_review_document.Document")
    mock_add_document_header = mocker.patch(
        "get_reports.create_review_document._add_document_header"
    )
    mock_add_county_records = mocker.patch(
        "get_reports.create_review_document._add_county_records"
    )

    observations = {
        "date of observations": "2023-01-01",
        "state": "Virginia",
        "date of report": "2023-01-02",
        "records": [{"county": "Fairfax", "records": []}],
    }

    result = _create_document(observations)

    mock_document.assert_called_once()
    mock_add_document_header.assert_called_once_with(
        mock_document.return_value, observations
    )
    mock_add_county_records.assert_called_once_with(
        mock_document.return_value, observations["records"]
    )
    assert result == mock_document.return_value


def test_create_document_missing_records(mocker):
    """Test _create_document with missing 'records' in observations."""
    mock_document = mocker.patch("get_reports.create_review_document.Document")
    mock_add_document_header = mocker.patch(
        "get_reports.create_review_document._add_document_header"
    )
    mock_add_county_records = mocker.patch(
        "get_reports.create_review_document._add_county_records"
    )

    observations = {
        "date of observations": "2023-01-01",
        "state": "Virginia",
        "date of report": "2023-01-02",
    }

    with pytest.raises(KeyError):
        _create_document(observations)

    mock_document.assert_called_once()
    mock_add_document_header.assert_called_once_with(
        mock_document.return_value, observations
    )
    mock_add_county_records.assert_not_called()


def test_add_document_header(mocker):
    """Test _add_document_header with valid observations."""
    mock_document = mocker.Mock()
    mock_add_heading = mock_document.add_heading
    mock_add_paragraph = mock_document.add_paragraph

    observations = {
        "date of observations": "2023-01-01",
        "region": "US-VA",
        "date of report": "2023-01-02",
    }

    _add_document_header(mock_document, observations)

    mock_add_heading.assert_called_once_with(
        "DRAFT Records for Expedited Review", 0
    )
    assert mock_add_paragraph.call_count == 5

    mock_add_paragraph.assert_any_call(
        style="List Bullet", text="Dates of observations: 2023-01-01"
    )
    mock_add_paragraph.assert_any_call(
        style=LIST_BULLET_STYLE, text="Region: US-VA"
    )
    mock_add_paragraph.assert_any_call(
        style=LIST_BULLET_STYLE, text="Dates of report creation: 2023-01-02"
    )

    # Check the hyperlinks
    produced_paragraph = mock_add_paragraph.call_args_list[3][1]
    assert produced_paragraph["style"] == LIST_BULLET_STYLE
    assert "Produced for and by VARCOM" in produced_paragraph["text"]

    generated_paragraph = mock_add_paragraph.call_args_list[4][1]
    assert generated_paragraph["style"] == LIST_BULLET_STYLE
    assert (
        "Automatically generated by VARCOM-get-reports"
        in generated_paragraph["text"]
    )


def test_add_county_records(mocker):
    """Test _add_county_records with valid county data."""
    mock_document = mocker.Mock()
    mock_add_heading = mock_document.add_heading
    mock_add_paragraph = mock_document.add_paragraph
    mock_add_species_records = mocker.patch(
        "get_reports.create_review_document._add_species_records"
    )

    counties = [
        {"county": "Fairfax", "records": [{"species": "Cardinal"}]},
        {
            "county": "Loudoun",
            "records": [{"species": "Blue Jay"}, {"species": "Robin"}],
        },
    ]

    _add_county_records(mock_document, counties)

    # Check that headings and paragraphs are added for each county
    assert mock_add_heading.call_count == 2
    mock_add_heading.assert_any_call("Reviewable records in Fairfax", level=1)
    mock_add_heading.assert_any_call("Reviewable records in Loudoun", level=1)

    assert mock_add_paragraph.call_count == 2
    mock_add_paragraph.assert_any_call("Total records: 1")
    mock_add_paragraph.assert_any_call("Total records: 2")

    # Check that _add_species_records is called for each county
    assert mock_add_species_records.call_count == 2
    mock_add_species_records.assert_any_call(mock_document, counties[0])
    mock_add_species_records.assert_any_call(mock_document, counties[1])


def test_add_county_records_empty_counties(mocker):
    """Test _add_county_records with an empty counties list."""
    mock_document = mocker.Mock()
    mock_add_heading = mock_document.add_heading
    mock_add_paragraph = mock_document.add_paragraph
    mock_add_species_records = mocker.patch(
        "get_reports.create_review_document._add_species_records"
    )

    counties = []

    _add_county_records(mock_document, counties)

    # Ensure no headings, paragraphs, or species records are added
    mock_add_heading.assert_not_called()
    mock_add_paragraph.assert_not_called()
    mock_add_species_records.assert_not_called()


def test_add_species_records_with_valid_data(mocker):
    """Test _add_species_records with valid county data."""
    mock_document = mocker.Mock()
    mock_add_species_heading = mocker.patch(
        "get_reports.create_review_document._add_species_heading"
    )
    mock_add_observation_data = mocker.patch(
        "get_reports.create_review_document._add_observation_data"
    )

    county = {
        "records": [
            {
                "media": True,
                "observation": {
                    "comName": "Cardinal",
                    "obsDt": "2023-01-01",
                    "subId": "S12345",
                },
            },
            {
                "media": True,
                "observation": {
                    "comName": "Cardinal",
                    "obsDt": "2023-01-02",
                    "subId": "S12346",
                },
            },
            {
                "media": True,
                "observation": {
                    "comName": "Blue Jay",
                    "obsDt": "2023-01-01",
                    "subId": "S12347",
                },
            },
        ]
    }

    _add_species_records(mock_document, county)

    # Check that _add_species_heading is called for each unique species
    assert mock_add_species_heading.call_count == 2
    mock_add_species_heading.assert_any_call(
        mock_document, "Cardinal", county["records"][0], county
    )
    mock_add_species_heading.assert_any_call(
        mock_document, "Blue Jay", county["records"][2], county
    )

    # Check that _add_observation_data is called once for each species with a subId
    assert mock_add_observation_data.call_count == 2
    mock_add_observation_data.assert_any_call(
        mock_document, county["records"][0]
    )
    mock_add_observation_data.assert_any_call(
        mock_document, county["records"][2]
    )


def test_add_species_records_with_empty_records(mocker):
    """Test _add_species_records with an empty records list."""
    mock_document = mocker.Mock()
    mock_add_species_heading = mocker.patch(
        "get_reports.create_review_document._add_species_heading"
    )
    mock_add_observation_data = mocker.patch(
        "get_reports.create_review_document._add_observation_data"
    )

    county = {"records": []}

    _add_species_records(mock_document, county)

    # Ensure no species headings or observation data are added
    mock_add_species_heading.assert_not_called()
    mock_add_observation_data.assert_not_called()


def test_add_species_records_with_missing_subId(mocker):
    """Test _add_species_records when some records are missing subId."""
    mock_document = mocker.Mock()
    mock_add_species_heading = mocker.patch(
        "get_reports.create_review_document._add_species_heading"
    )
    mock_add_observation_data = mocker.patch(
        "get_reports.create_review_document._add_observation_data"
    )

    county = {
        "records": [
            {
                "media": True,
                "observation": {
                    "comName": "Cardinal",
                    "obsDt": "2023-01-01",
                },
            },
            {
                "media": True,
                "observation": {
                    "comName": "Blue Jay",
                    "obsDt": "2023-01-02",
                    "subId": "S12345",
                },
            },
        ]
    }

    _add_species_records(mock_document, county)

    # Check that _add_species_heading is called for each unique species
    assert mock_add_species_heading.call_count == 2
    mock_add_species_heading.assert_any_call(
        mock_document, "Cardinal", county["records"][0], county
    )
    mock_add_species_heading.assert_any_call(
        mock_document, "Blue Jay", county["records"][1], county
    )

    # Check that _add_observation_data is only called for records with a subId
    assert mock_add_observation_data.call_count == 1
    mock_add_observation_data.assert_any_call(
        mock_document, county["records"][1]
    )


def test_add_species_heading_exclude_only_notes(mocker):
    """Test _add_species_heading with exclude, only, and uniqueExcludeNotes."""
    mock_document = mocker.Mock()
    mock_add_heading = mock_document.add_heading
    mock_add_paragraph = mock_document.add_paragraph

    species = "Cardinal"
    record = {
        "review_species": {
            "exclude": ["County A", "County B"],
            "only": ["County C"],
            "uniqueExcludeNotes": "Special note about exclusion.",
        }
    }
    county = {"county": "Fairfax"}

    _add_species_heading(mock_document, species, record, county)

    mock_add_heading.assert_called_once_with(species, level=2)
    assert mock_add_paragraph.call_count == 3

    mock_add_paragraph.assert_any_call(
        "The species Cardinal is not excluded from review in Fairfax because it is not in the following counties or groups of counties: ['County A', 'County B']"
    )
    mock_add_paragraph.assert_any_call(
        "The species Cardinal: is only reviewed in the following counties or groups of counties: ['County C']"
    )
    mock_add_paragraph.assert_any_call(
        "This species has unique Exclude Notes which could not be automated. Special note about exclusion."
    )


def test_add_species_heading_reviewable_statewide(mocker):
    """Test _add_species_heading when species is reviewable statewide."""
    mock_document = mocker.Mock()
    mock_add_heading = mocker.Mock()
    mock_add_paragraph = mocker.Mock()
    mock_document.add_heading = mock_add_heading
    mock_document.add_paragraph = mock_add_paragraph

    species = "Blue Jay"
    record = {"review_species": {}}
    county = {"county": "Loudoun"}

    _add_species_heading(mock_document, species, record, county)

    mock_add_heading.assert_called_once_with(species, level=2)
    mock_add_paragraph.assert_called_once_with(
        "The species Blue Jay is reviewable across the entire state."
    )


def test_add_species_heading_new_species(mocker):
    """Test _add_species_heading when species is new to the state list."""
    mock_document = mocker.Mock()
    mock_add_heading = mocker.Mock()
    mock_add_paragraph = mocker.Mock()
    mock_document.add_heading = mock_add_heading
    mock_document.add_paragraph = mock_add_paragraph

    species = "Rare Bird"
    record = {"review_species": {}, "new": True}
    county = {"county": "Richmond"}

    _add_species_heading(mock_document, species, record, county)

    mock_add_heading.assert_called_once_with(species, level=2)
    assert any(
        "The species Rare Bird is not in the state list. A new record?"
        in call.args[0]
        for call in mock_add_paragraph.call_args_list
    )


def test_add_species_heading_combined_conditions(mocker):
    """Test _add_species_heading with multiple conditions."""
    mock_document = mocker.Mock()
    mock_add_heading = mocker.Mock()
    mock_add_paragraph = mocker.Mock()
    mock_document.add_heading = mock_add_heading
    mock_document.add_paragraph = mock_add_paragraph

    species = "Eagle"
    record = {
        "review_species": {"exclude": ["County X"], "only": ["County Y"]},
        "new": True,
    }
    county = {"county": "Arlington"}

    _add_species_heading(mock_document, species, record, county)

    mock_add_heading.assert_called_once_with(species, level=2)
    assert mock_add_paragraph.call_count == 3

    mock_add_paragraph.assert_any_call(
        "The species Eagle is not excluded from review in Arlington because it is not in the following counties or groups of counties: ['County X']"
    )
    mock_add_paragraph.assert_any_call(
        "The species Eagle: is only reviewed in the following counties or groups of counties: ['County Y']"
    )
    mock_add_paragraph.assert_any_call(
        "The species Eagle is not in the state list. A new record?"
    )


def test_add_observation_data_with_media(mocker):
    """Test _add_observation_data when the record has media."""
    mock_document = mocker.Mock()
    mock_paragraph = mocker.Mock()
    mock_run = mocker.Mock()
    mock_document.add_paragraph.return_value = mock_paragraph
    mock_paragraph.add_run.return_value = mock_run

    record = {
        "observation": {
            "subId": "S12345",
            "obsDt": "2023-01-01",
        },
        "media": True,
    }

    _add_observation_data(mock_document, record)

    mock_document.add_paragraph.assert_called_once_with(style="List Bullet")
    mock_paragraph.add_run.assert_called_once_with(
        "2023-01-01, Has media., Checklist: https://ebird.org/checklist/S12345"
    )
    assert mock_run.hyperlink == "https://ebird.org/checklist/S12345"


def test_add_observation_data_without_media(mocker):
    """Test _add_observation_data when the record does not have media."""
    mock_document = mocker.Mock()
    mock_paragraph = mocker.Mock()
    mock_run = mocker.Mock()
    mock_document.add_paragraph.return_value = mock_paragraph
    mock_paragraph.add_run.return_value = mock_run

    record = {
        "observation": {
            "subId": "S12345",
            "obsDt": "2023-01-01",
        },
    }

    _add_observation_data(mock_document, record)

    mock_document.add_paragraph.assert_called_once_with(style="List Bullet")
    mock_paragraph.add_run.assert_called_once_with(
        "2023-01-01, No media., Checklist: https://ebird.org/checklist/S12345"
    )
    assert mock_run.hyperlink == "https://ebird.org/checklist/S12345"


def test_add_observation_data_missing_subId(mocker):
    """Test _add_observation_data when the record is missing subId."""
    mock_document = mocker.Mock()
    mock_paragraph = mocker.Mock()
    mock_document.add_paragraph.return_value = mock_paragraph

    record = {
        "observation": {
            "obsDt": "2023-01-01",
        },
    }

    with pytest.raises(KeyError, match="'subId'"):
        _add_observation_data(mock_document, record)

    mock_document.add_paragraph.assert_called_once_with(style="List Bullet")
    mock_paragraph.add_run.assert_not_called()


def test_add_observation_data_missing_obsDt(mocker):
    """Test _add_observation_data when the record is missing obsDt."""
    mock_document = mocker.Mock()
    mock_paragraph = mocker.Mock()
    mock_document.add_paragraph.return_value = mock_paragraph

    record = {
        "observation": {
            "subId": "S12345",
        },
    }

    with pytest.raises(KeyError, match="'obsDt'"):
        _add_observation_data(mock_document, record)

    mock_document.add_paragraph.assert_called_once_with(style="List Bullet")
    mock_paragraph.add_run.assert_not_called()


def test_save_document_file_exists(mocker, tmp_path):
    """Test _save_document when the output file already exists."""
    mock_document = mocker.Mock()
    mock_remove = mocker.patch("os.remove")
    mock_exists = mocker.patch("os.path.exists", return_value=True)

    output = tmp_path / "test.docx"

    _save_document(mock_document, str(output))

    mock_exists.assert_called_once_with(str(output))
    mock_remove.assert_called_once_with(str(output))
    mock_document.save.assert_called_once_with(str(output))


def test_save_document_file_does_not_exist(mocker, tmp_path):
    """Test _save_document when the output file does not exist."""
    mock_document = mocker.Mock()
    mock_remove = mocker.patch("os.remove")
    mock_exists = mocker.patch("os.path.exists", return_value=False)

    output = tmp_path / "test.docx"

    _save_document(mock_document, str(output))

    mock_exists.assert_called_once_with(str(output))
    mock_remove.assert_not_called()
    mock_document.save.assert_called_once_with(str(output))


def test_main_valid_arguments(mocker):
    """Test main function with valid arguments."""
    mock_parse_arguments = mocker.patch(
        "get_reports.create_review_document._parse_arguments"
    )
    mock_load_observations = mocker.patch(
        "get_reports.create_review_document._load_observations"
    )
    mock_create_document = mocker.patch(
        "get_reports.create_review_document._create_document"
    )
    mock_save_document = mocker.patch(
        "get_reports.create_review_document._save_document"
    )
    mock_logging = mocker.patch("logging.basicConfig")

    # Mock arguments
    mock_parse_arguments.return_value = argparse.Namespace(
        input="valid_records.json",
        output="output.docx",
        verbose=True,
    )

    # Mock return values
    mock_load_observations.return_value = {"key": "value"}
    mock_create_document.return_value = "mock_document"

    # Call the main function
    main()

    # Assertions
    mock_parse_arguments.assert_called_once()
    mock_logging.assert_called_once_with(level=logging.INFO)
    mock_load_observations.assert_called_once_with("valid_records.json")
    mock_create_document.assert_called_once_with({"key": "value"})
    mock_save_document.assert_called_once_with("mock_document", "output.docx")


def test_main_no_verbose(mocker):
    """Test main function without verbose logging."""
    mock_parse_arguments = mocker.patch(
        "get_reports.create_review_document._parse_arguments"
    )
    mock_load_observations = mocker.patch(
        "get_reports.create_review_document._load_observations"
    )
    mock_create_document = mocker.patch(
        "get_reports.create_review_document._create_document"
    )
    mock_save_document = mocker.patch(
        "get_reports.create_review_document._save_document"
    )
    mock_logging = mocker.patch("logging.basicConfig")

    # Mock arguments
    mock_parse_arguments.return_value = argparse.Namespace(
        input="valid_records.json",
        output="output.docx",
        verbose=False,
    )

    # Mock return values
    mock_load_observations.return_value = {"key": "value"}
    mock_create_document.return_value = "mock_document"

    # Call the main function
    main()

    # Assertions
    mock_parse_arguments.assert_called_once()
    mock_logging.assert_not_called()
    mock_load_observations.assert_called_once_with("valid_records.json")
    mock_create_document.assert_called_once_with({"key": "value"})
    mock_save_document.assert_called_once_with("mock_document", "output.docx")


def test_main_load_observations_raises_exception(mocker):
    """Test main function when _load_observations raises an exception."""
    mock_parse_arguments = mocker.patch(
        "get_reports.create_review_document._parse_arguments"
    )
    mock_load_observations = mocker.patch(
        "get_reports.create_review_document._load_observations"
    )
    mock_logging = mocker.patch("logging.basicConfig")

    # Mock arguments
    mock_parse_arguments.return_value = argparse.Namespace(
        input="invalid_records.json",
        output="output.docx",
        verbose=True,
    )

    # Mock exception
    mock_load_observations.side_effect = FileNotFoundError("File not found")

    # Call the main function and assert exception is raised
    with pytest.raises(FileNotFoundError, match="File not found"):
        main()

    # Assertions
    mock_parse_arguments.assert_called_once()
    mock_logging.assert_called_once_with(level=logging.INFO)
    mock_load_observations.assert_called_once_with("invalid_records.json")
