import json
import logging
from unittest.mock import mock_open, patch

from get_reports.get_review_rules import (
    _check_counties_in_groups,
    _check_exclusions_in_counties,
    _check_species_in_taxonomy,
    get_review_rules,
)


def test_check_counties_in_groups_no_warnings(caplog):
    county_list = [{"name": "CountyA"}, {"name": "CountyB"}]
    review_species = {"county_groups": [{"counties": ["CountyA", "CountyB"]}]}

    with caplog.at_level(logging.WARNING):
        _check_counties_in_groups(county_list, review_species)

    assert len(caplog.records) == 0


def test_check_counties_in_groups_county_not_in_any_group(caplog):
    county_list = [
        {"name": "CountyA"},
        {"name": "CountyB"},
        {"name": "CountyC"},
    ]
    review_species = {"county_groups": [{"counties": ["CountyA", "CountyB"]}]}

    with caplog.at_level(logging.WARNING):
        _check_counties_in_groups(county_list, review_species)

    assert len(caplog.records) == 1
    assert "County CountyC not found in any county group" in caplog.text


def test_check_counties_in_groups_county_in_multiple_groups(caplog):
    county_list = [{"name": "CountyA"}, {"name": "CountyB"}]
    review_species = {
        "county_groups": [
            {"counties": ["CountyA", "CountyB"]},
            {"counties": ["CountyA"]},
        ]
    }

    with caplog.at_level(logging.WARNING):
        _check_counties_in_groups(county_list, review_species)

    assert len(caplog.records) == 1
    assert "County CountyA found in multiple county groups" in caplog.text


def test_check_counties_in_groups_mixed_warnings(caplog):
    county_list = [
        {"name": "CountyA"},
        {"name": "CountyB"},
        {"name": "CountyC"},
    ]
    review_species = {
        "county_groups": [
            {"counties": ["CountyA", "CountyB"]},
            {"counties": ["CountyA"]},
        ]
    }

    with caplog.at_level(logging.WARNING):
        _check_counties_in_groups(county_list, review_species)

    assert len(caplog.records) == 2
    assert "County CountyA found in multiple county groups" in caplog.text
    assert "County CountyC not found in any county group" in caplog.text


def test_check_species_in_taxonomy_no_warnings(caplog):
    review_species = {
        "review_species": [
            {"comName": "SpeciesA"},
            {"comName": "SpeciesB"},
        ]
    }
    taxonomy = [
        {"comName": "SpeciesA"},
        {"comName": "SpeciesB"},
        {"comName": "SpeciesC"},
    ]

    with caplog.at_level(logging.WARNING):
        _check_species_in_taxonomy(review_species, taxonomy)

    assert len(caplog.records) == 0


def test_check_species_in_taxonomy_species_not_in_taxonomy(caplog):
    review_species = {
        "review_species": [
            {"comName": "SpeciesA"},
            {"comName": "SpeciesD"},
        ]
    }
    taxonomy = [
        {"comName": "SpeciesA"},
        {"comName": "SpeciesB"},
        {"comName": "SpeciesC"},
    ]

    with caplog.at_level(logging.WARNING):
        _check_species_in_taxonomy(review_species, taxonomy)

    assert len(caplog.records) == 1
    assert "Species SpeciesD not found in eBird taxonomy" in caplog.text


def test_check_species_in_taxonomy_multiple_warnings(caplog):
    review_species = {
        "review_species": [
            {"comName": "SpeciesX"},
            {"comName": "SpeciesY"},
        ]
    }
    taxonomy = [
        {"comName": "SpeciesA"},
        {"comName": "SpeciesB"},
        {"comName": "SpeciesC"},
    ]

    with caplog.at_level(logging.WARNING):
        _check_species_in_taxonomy(review_species, taxonomy)

    assert len(caplog.records) == 2
    assert "Species SpeciesX not found in eBird taxonomy" in caplog.text
    assert "Species SpeciesY not found in eBird taxonomy" in caplog.text


def test_check_species_in_taxonomy_logs_info_message(caplog):
    review_species = {
        "review_species": [
            {"comName": "SpeciesA"},
        ]
    }
    taxonomy = [
        {"comName": "SpeciesA"},
        {"comName": "SpeciesB"},
    ]

    with caplog.at_level(logging.INFO):
        _check_species_in_taxonomy(review_species, taxonomy)

    assert any(
        "Checking species in state review list against eBird taxonomy."
        in record.message
        for record in caplog.records
    )


def test_check_exclusions_in_counties_no_warnings(caplog):
    review_species = {
        "county_groups": [
            {"name": "GroupA", "counties": ["CountyA", "CountyB"]}
        ],
        "review_species": [
            {"comName": "SpeciesA", "exclude": ["CountyA", "GroupA"]}
        ],
    }
    county_list = [{"name": "CountyA"}, {"name": "CountyB"}]
    state = "TestState"

    with caplog.at_level(logging.WARNING):
        _check_exclusions_in_counties(review_species, county_list, state)

    assert len(caplog.records) == 0


def test_check_exclusions_in_counties_county_not_in_county_list(caplog):
    review_species = {
        "county_groups": [
            {"name": "GroupA", "counties": ["CountyA", "CountyC"]}
        ],
        "review_species": [],
    }
    county_list = [{"name": "CountyA"}, {"name": "CountyB"}]
    state = "TestState"

    with caplog.at_level(logging.WARNING):
        _check_exclusions_in_counties(review_species, county_list, state)

    assert len(caplog.records) == 1
    assert (
        "County CountyC not found in eBird list of counties for TestState."
        in caplog.text
    )


def test_check_exclusions_in_counties_exclusion_not_found(caplog):
    review_species = {
        "county_groups": [
            {"name": "GroupA", "counties": ["CountyA", "CountyB"]}
        ],
        "review_species": [
            {"comName": "SpeciesA", "exclude": ["CountyC", "GroupB"]}
        ],
    }
    county_list = [{"name": "CountyA"}, {"name": "CountyB"}]
    state = "TestState"

    with caplog.at_level(logging.WARNING):
        _check_exclusions_in_counties(review_species, county_list, state)

    assert len(caplog.records) == 2
    assert "Exclusion CountyC was not found as a group or county" in caplog.text
    assert "Exclusion GroupB was not found as a group or county" in caplog.text


def test_check_exclusions_in_counties_mixed_warnings(caplog):
    review_species = {
        "county_groups": [
            {"name": "GroupA", "counties": ["CountyA", "CountyC"]}
        ],
        "review_species": [
            {"comName": "SpeciesA", "exclude": ["CountyC", "GroupB"]}
        ],
    }
    county_list = [{"name": "CountyA"}, {"name": "CountyB"}]
    state = "TestState"

    with caplog.at_level(logging.WARNING):
        _check_exclusions_in_counties(review_species, county_list, state)

    assert len(caplog.records) == 3
    assert (
        "County CountyC not found in eBird list of counties for TestState."
        in caplog.text
    )
    assert "Exclusion CountyC was not found as a group or county" in caplog.text
    assert "Exclusion GroupB was not found as a group or county" in caplog.text


def test_get_review_rules_file_not_exist(caplog):
    file_name = "non_existent_file.json"
    taxonomy = []
    county_list = []
    state = "TestState"

    with caplog.at_level(logging.ERROR):
        result = get_review_rules(file_name, taxonomy, county_list, state)

    assert result == {}
    assert len(caplog.records) == 1
    assert f"File {file_name} does not exist." in caplog.text


def test_get_review_rules_valid_file():
    file_name = "valid_file.json"
    taxonomy = [{"comName": "SpeciesA"}]
    county_list = [{"name": "CountyA"}]
    state = "TestState"
    mock_data = {
        "county_groups": [{"name": "GroupA", "counties": ["CountyA"]}],
        "review_species": [{"comName": "SpeciesA", "exclude": ["GroupA"]}],
    }

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
        with patch("os.path.exists", return_value=True):
            result = get_review_rules(file_name, taxonomy, county_list, state)

    assert result == mock_data


def test_get_review_rules_invalid_json():
    file_name = "invalid_file.json"
    taxonomy = []
    county_list = []
    state = "TestState"

    with patch("builtins.open", mock_open(read_data="invalid json")):
        with patch("os.path.exists", return_value=True):
            try:
                get_review_rules(file_name, taxonomy, county_list, state)
            except json.JSONDecodeError:
                assert True
            else:
                assert False


def test_get_review_rules_validation_functions_called():
    file_name = "valid_file.json"
    taxonomy = [{"comName": "SpeciesA"}]
    county_list = [{"name": "CountyA"}]
    state = "TestState"
    mock_data = {
        "county_groups": [{"name": "GroupA", "counties": ["CountyA"]}],
        "review_species": [{"comName": "SpeciesA", "exclude": ["GroupA"]}],
    }

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
        with patch("os.path.exists", return_value=True):
            with (
                patch(
                    "get_reports.get_review_rules._check_counties_in_groups"
                ) as mock_check_counties,
                patch(
                    "get_reports.get_review_rules._check_species_in_taxonomy"
                ) as mock_check_species,
                patch(
                    "get_reports.get_review_rules._check_exclusions_in_counties"
                ) as mock_check_exclusions,
            ):
                get_review_rules(file_name, taxonomy, county_list, state)

                mock_check_counties.assert_called_once_with(
                    county_list, mock_data
                )
                mock_check_species.assert_called_once_with(mock_data, taxonomy)
                mock_check_exclusions.assert_called_once_with(
                    mock_data, county_list, state
                )
