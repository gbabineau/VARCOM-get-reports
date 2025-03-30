from get_reports.get_records_to_review import (
    _county_in_list_or_group,
    _reviewable_species,
    _is_new_record,
    _reviewable_species_with_no_exclusions,
    _find_record_of_interest,
    _iterate_days_in_month,
    get_records_to_review,
)
from datetime import date
from unittest.mock import patch


def test_county_in_exclusion_list():
    county_name = "CountyA"
    exclusion_list = ["CountyA", "CountyB"]
    county_groups = []
    assert (
        _county_in_list_or_group(county_name, exclusion_list, county_groups)
        is True
    )


def test_county_in_group_in_exclusion_list():
    county_name = "CountyC"
    exclusion_list = ["Group1"]
    county_groups = [{"name": "Group1", "counties": ["CountyC", "CountyD"]}]
    assert (
        _county_in_list_or_group(county_name, exclusion_list, county_groups)
        is True
    )


def test_county_not_in_exclusion_list_or_group():
    county_name = "CountyE"
    exclusion_list = ["CountyA", "CountyB"]
    county_groups = [{"name": "Group1", "counties": ["CountyC", "CountyD"]}]
    assert (
        _county_in_list_or_group(county_name, exclusion_list, county_groups)
        is False
    )


def test_county_in_multiple_groups():
    county_name = "CountyF"
    exclusion_list = ["Group1", "Group2"]
    county_groups = [
        {"name": "Group1", "counties": ["CountyE", "CountyF"]},
        {"name": "Group2", "counties": ["CountyF", "CountyG"]},
    ]
    assert (
        _county_in_list_or_group(county_name, exclusion_list, county_groups)
        is True
    )


def test_empty_exclusion_list_and_groups():
    county_name = "CountyH"
    exclusion_list = []
    county_groups = []
    assert (
        _county_in_list_or_group(county_name, exclusion_list, county_groups)
        is False
    )


def test_is_new_record_not_exotic_and_not_in_state_list():
    observation = {"comName": "SpeciesA", "exoticCategory": ""}
    state_list = [{"comName": "SpeciesB"}, {"comName": "SpeciesC"}]
    assert _is_new_record(observation, state_list) is True


def test_is_new_record_exotic():
    observation = {"comName": "SpeciesA", "exoticCategory": "X"}
    state_list = [{"comName": "SpeciesB"}, {"comName": "SpeciesC"}]
    assert _is_new_record(observation, state_list) is False


def test_is_new_record_in_state_list():
    observation = {"comName": "SpeciesA", "exoticCategory": ""}
    state_list = [{"comName": "SpeciesA"}, {"comName": "SpeciesC"}]
    assert _is_new_record(observation, state_list) is False


def test_is_new_record_exotic_and_in_state_list():
    observation = {"comName": "SpeciesA", "exoticCategory": "X"}
    state_list = [{"comName": "SpeciesA"}, {"comName": "SpeciesC"}]
    assert _is_new_record(observation, state_list) is False


def test_reviewable_species_match():
    observation = {"comName": "SpeciesA"}
    species_to_review = [{"comName": "SpeciesA"}, {"comName": "SpeciesB"}]
    assert _reviewable_species(observation, species_to_review) is not None


def test_reviewable_species_no_match():
    observation = {"comName": "SpeciesC"}
    species_to_review = [{"comName": "SpeciesA"}, {"comName": "SpeciesB"}]
    assert _reviewable_species(observation, species_to_review) is None


def test_reviewable_species_empty_review_list():
    observation = {"comName": "SpeciesA"}
    species_to_review = []
    assert _reviewable_species(observation, species_to_review) is None


def test_reviewable_species_with_no_exclusions_only_match():
    matching_species = {"only": ["CountyA", "CountyB"]}
    review_species = {"county_groups": ["CountyA"]}
    county = {"name": "CountyA"}
    assert (
        _reviewable_species_with_no_exclusions(
            matching_species, review_species, county
        )
        is True
    )


def test_reviewable_species_with_no_exclusions_only_no_match():
    matching_species = {"only": ["CountyA", "CountyB"]}
    review_species = {"county_groups": []}
    county = {"name": "CountyC"}
    assert (
        _reviewable_species_with_no_exclusions(
            matching_species, review_species, county
        )
        is False
    )


def test_reviewable_species_with_no_exclusions_exclude_match():
    matching_species = {"exclude": ["CountyA", "CountyB"]}
    review_species = {"county_groups": []}
    county = {"name": "CountyA"}
    assert (
        _reviewable_species_with_no_exclusions(
            matching_species, review_species, county
        )
        is False
    )


def test_reviewable_species_with_no_exclusions_exclude_no_match():
    matching_species = {"exclude": ["CountyA", "CountyB"]}
    review_species = {"county_groups": []}
    county = {"name": "CountyC"}
    assert (
        _reviewable_species_with_no_exclusions(
            matching_species, review_species, county
        )
        is True
    )


def test_reviewable_species_with_no_exclusions_only_with_group_match():
    matching_species = {"only": ["Group1"]}
    review_species = {
        "county_groups": [
            {"name": "Group1", "counties": ["CountyA", "CountyB"]}
        ]
    }
    county = {"name": "CountyA"}
    assert (
        _reviewable_species_with_no_exclusions(
            matching_species, review_species, county
        )
        is True
    )


def test_reviewable_species_with_no_exclusions_only_with_group_no_match():
    matching_species = {"only": ["Group1"]}
    review_species = {
        "county_groups": [
            {"name": "Group1", "counties": ["CountyA", "CountyB"]}
        ]
    }
    county = {"name": "CountyC"}
    assert (
        _reviewable_species_with_no_exclusions(
            matching_species, review_species, county
        )
        is False
    )


def test_reviewable_species_with_no_exclusions_exclude_with_group_match():
    matching_species = {"exclude": ["Group1"]}
    review_species = {
        "county_groups": [
            {"name": "Group1", "counties": ["CountyA", "CountyB"]}
        ]
    }
    county = {"name": "CountyA"}
    assert (
        _reviewable_species_with_no_exclusions(
            matching_species, review_species, county
        )
        is False
    )


def test_reviewable_species_with_no_exclusions_exclude_with_group_no_match():
    matching_species = {"exclude": ["Group1"]}
    review_species = {
        "county_groups": [
            {"name": "Group1", "counties": ["CountyA", "CountyB"]}
        ]
    }
    county = {"name": "CountyC"}
    assert (
        _reviewable_species_with_no_exclusions(
            matching_species, review_species, county
        )
        is True
    )


def test_reviewable_species_with_no_exclusions_no_only_or_exclude():
    matching_species = {}
    review_species = {"county_groups": []}
    county = {"name": "CountyA"}
    assert (
        _reviewable_species_with_no_exclusions(
            matching_species, review_species, county
        )
        is True
    )


@patch("get_reports.get_records_to_review.get_historic_observations")
def test_find_record_of_interest_new_record(mock_get_historic_observations):
    ebird_api_key = "test_key"
    state_list = [{"comName": "SpeciesB"}]
    county = {"code": "CountyCode", "name": "CountyName"}
    day = date(2023, 10, 1)
    review_species = {"review_species": []}

    mock_get_historic_observations.return_value = [
        {"comName": "SpeciesA", "exoticCategory": ""}
    ]

    result = _find_record_of_interest(
        ebird_api_key, state_list, county, day, review_species
    )

    assert len(result) == 1
    assert result[0]["observation"]["comName"] == "SpeciesA"
    assert result[0]["new"] is True


@patch("get_reports.get_records_to_review.get_historic_observations")
def test_find_record_of_interest_reviewable_species(
    mock_get_historic_observations,
):
    ebird_api_key = "test_key"
    state_list = [{"comName": "SpeciesA"}]
    county = {"code": "CountyCode", "name": "CountyName"}
    day = date(2023, 10, 1)
    review_species = {
        "review_species": [{"comName": "SpeciesA", "only": ["CountyName"]}],
        "county_groups": [],
    }

    mock_get_historic_observations.return_value = [
        {"comName": "SpeciesA", "exoticCategory": ""}
    ]

    result = _find_record_of_interest(
        ebird_api_key, state_list, county, day, review_species
    )

    assert len(result) == 1
    assert result[0]["observation"]["comName"] == "SpeciesA"
    assert result[0]["new"] is False
    assert result[0]["reviewable"] is True
    assert result[0]["review_species"]["comName"] == "SpeciesA"


@patch("get_reports.get_records_to_review.get_historic_observations")
def test_find_record_of_interest_no_records(mock_get_historic_observations):
    ebird_api_key = "test_key"
    state_list = [{"comName": "SpeciesB"}]
    county = {"code": "CountyCode", "name": "CountyName"}
    day = date(2023, 10, 1)
    review_species = {"review_species": [], "county_groups": []}

    mock_get_historic_observations.return_value = []

    result = _find_record_of_interest(
        ebird_api_key, state_list, county, day, review_species
    )

    assert len(result) == 0


@patch("get_reports.get_records_to_review.get_historic_observations")
def test_find_record_of_interest_excluded_species(
    mock_get_historic_observations,
):
    ebird_api_key = "test_key"
    state_list = [{"comName": "SpeciesA"}]
    county = {"code": "CountyCode", "name": "CountyName"}
    day = date(2023, 10, 1)
    review_species = {
        "review_species": [{"comName": "SpeciesA", "exclude": ["CountyName"]}],
        "county_groups": [],
    }

    mock_get_historic_observations.return_value = [
        {"comName": "SpeciesA", "exoticCategory": ""}
    ]

    result = _find_record_of_interest(
        ebird_api_key, state_list, county, day, review_species
    )

    assert len(result) == 0


def test_iterate_days_in_month_full_month():
    year = 2023
    month = 2  # February
    day = 0  # Full month
    days = list(_iterate_days_in_month(year, month, day))
    assert len(days) == 28  # 2023 is not a leap year
    assert days[0] == date(2023, 2, 1)
    assert days[-1] == date(2023, 2, 28)


def test_iterate_days_in_month_specific_day():
    year = 2023
    month = 2  # February
    day = 15  # Specific day
    days = list(_iterate_days_in_month(year, month, day))
    assert len(days) == 1
    assert days[0] == date(2023, 2, 15)


def test_iterate_days_in_month_full_month_leap_year():
    year = 2024
    month = 2  # February
    day = 0  # Full month
    days = list(_iterate_days_in_month(year, month, day))
    assert len(days) == 29  # 2024 is a leap year
    assert days[0] == date(2024, 2, 1)
    assert days[-1] == date(2024, 2, 29)


def test_iterate_days_in_month_specific_day_leap_year():
    year = 2024
    month = 2  # February
    day = 29  # Specific day
    days = list(_iterate_days_in_month(year, month, day))
    assert len(days) == 1
    assert days[0] == date(2024, 2, 29)


def test_iterate_days_in_month_full_month_31_days():
    year = 2023
    month = 7  # July
    day = 0  # Full month
    days = list(_iterate_days_in_month(year, month, day))
    assert len(days) == 31
    assert days[0] == date(2023, 7, 1)
    assert days[-1] == date(2023, 7, 31)


def test_iterate_days_in_month_specific_day_31_days():
    year = 2023
    month = 7  # July
    day = 15  # Specific day
    days = list(_iterate_days_in_month(year, month, day))
    assert len(days) == 1
    assert days[0] == date(2023, 7, 15)


def test_iterate_days_in_month_full_month_30_days():
    year = 2023
    month = 6  # June
    day = 0  # Full month
    days = list(_iterate_days_in_month(year, month, day))
    assert len(days) == 30
    assert days[0] == date(2023, 6, 1)
    assert days[-1] == date(2023, 6, 30)


def test_iterate_days_in_month_specific_day_30_days():
    year = 2023
    month = 6  # June
    day = 15  # Specific day
    days = list(_iterate_days_in_month(year, month, day))
    assert len(days) == 1
    assert days[0] == date(2023, 6, 15)


@patch("get_reports.get_records_to_review._iterate_days_in_month")
@patch("get_reports.get_records_to_review._find_record_of_interest")
def test_get_records_to_review_single_county_single_day(
    mock_find_record_of_interest, mock_iterate_days_in_month
):
    ebird_api_key = "test_key"
    state_list = [{"comName": "SpeciesA"}]
    counties = [{"name": "CountyA", "code": "CountyCodeA"}]
    year = 2023
    month = 10
    day = 1
    review_species = {"review_species": [], "county_groups": []}

    mock_iterate_days_in_month.return_value = [date(2023, 10, 1)]
    mock_find_record_of_interest.return_value = [
        {"observation": {"comName": "SpeciesB"}, "new": True}
    ]

    result = get_records_to_review(
        ebird_api_key, state_list, counties, year, month, day, review_species
    )

    assert len(result) == 1
    assert result[0]["county"] == "CountyA"
    assert len(result[0]["records"]) == 1
    assert result[0]["records"][0]["observation"]["comName"] == "SpeciesB"
    assert result[0]["records"][0]["new"] is True


@patch("get_reports.get_records_to_review._iterate_days_in_month")
@patch("get_reports.get_records_to_review._find_record_of_interest")
def test_get_records_to_review_multiple_counties(
    mock_find_record_of_interest, mock_iterate_days_in_month
):
    ebird_api_key = "test_key"
    state_list = [{"comName": "SpeciesA"}]
    counties = [
        {"name": "CountyA", "code": "CountyCodeA"},
        {"name": "CountyB", "code": "CountyCodeB"},
    ]
    year = 2023
    month = 10
    day = 1
    review_species = {"review_species": [], "county_groups": []}

    mock_iterate_days_in_month.return_value = [date(2023, 10, 1)]
    mock_find_record_of_interest.side_effect = [
        [{"observation": {"comName": "SpeciesB"}, "new": True}],
        [{"observation": {"comName": "SpeciesC"}, "new": False}],
    ]

    result = get_records_to_review(
        ebird_api_key, state_list, counties, year, month, day, review_species
    )

    assert len(result) == 2
    assert result[0]["county"] == "CountyA"
    assert len(result[0]["records"]) == 1
    assert result[0]["records"][0]["observation"]["comName"] == "SpeciesB"
    assert result[0]["records"][0]["new"] is True

    assert result[1]["county"] == "CountyB"
    assert len(result[1]["records"]) == 1
    assert result[1]["records"][0]["observation"]["comName"] == "SpeciesC"
    assert result[1]["records"][0]["new"] is False


@patch("get_reports.get_records_to_review._iterate_days_in_month")
@patch("get_reports.get_records_to_review._find_record_of_interest")
def test_get_records_to_review_no_records(
    mock_find_record_of_interest, mock_iterate_days_in_month
):
    ebird_api_key = "test_key"
    state_list = [{"comName": "SpeciesA"}]
    counties = [{"name": "CountyA", "code": "CountyCodeA"}]
    year = 2023
    month = 10
    day = 1
    review_species = {"review_species": [], "county_groups": []}

    mock_iterate_days_in_month.return_value = [date(2023, 10, 1)]
    mock_find_record_of_interest.return_value = []

    result = get_records_to_review(
        ebird_api_key, state_list, counties, year, month, day, review_species
    )

    assert len(result) == 0


@patch("get_reports.get_records_to_review._iterate_days_in_month")
@patch("get_reports.get_records_to_review._find_record_of_interest")
def test_get_records_to_review_multiple_days(
    mock_find_record_of_interest, mock_iterate_days_in_month
):
    ebird_api_key = "test_key"
    state_list = [{"comName": "SpeciesA"}]
    counties = [{"name": "CountyA", "code": "CountyCodeA"}]
    year = 2023
    month = 10
    day = 0  # Full month
    review_species = {"review_species": [], "county_groups": []}

    mock_iterate_days_in_month.return_value = [
        date(2023, 10, 1),
        date(2023, 10, 2),
    ]
    mock_find_record_of_interest.side_effect = [
        [{"observation": {"comName": "SpeciesB"}, "new": True}],
        [{"observation": {"comName": "SpeciesC"}, "new": False}],
    ]

    result = get_records_to_review(
        ebird_api_key, state_list, counties, year, month, day, review_species
    )

    assert len(result) == 1
    assert result[0]["county"] == "CountyA"
    assert len(result[0]["records"]) == 2
    assert result[0]["records"][0]["observation"]["comName"] == "SpeciesB"
    assert result[0]["records"][0]["new"] is True
    assert result[0]["records"][1]["observation"]["comName"] == "SpeciesC"
    assert result[0]["records"][1]["new"] is False
