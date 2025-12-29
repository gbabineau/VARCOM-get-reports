# tests/test_get_records_to_review_main.py
# pylint: disable=W0613, W0212, C0116, C0114, C0115
from datetime import date
from unittest.mock import patch

from get_reports.get_records_to_review import (
    _county_in_list_or_group,
    _find_record_of_interest,
    _get_checklist_with_retry,
    _get_historic_observations_with_retry,
    _is_new_record,
    _iterate_days_in_month,
    _observation_has_media,
    _pelagic_record,
    _reviewable_species,
    _reviewable_species_with_no_exclusions,
    get_records_to_review,
)


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
@patch("get_reports.get_records_to_review._is_new_record")
@patch("get_reports.get_records_to_review._pelagic_record")
@patch("get_reports.get_records_to_review._observation_has_media")
@patch("get_reports.get_records_to_review._reviewable_species")
@patch(
    "get_reports.get_records_to_review._reviewable_species_with_no_exclusions"
)
def test_find_record_of_interest_new_record(
    mock_reviewable_species_with_no_exclusions,
    mock_reviewable_species,
    mock_observation_has_media,
    mock_pelagic_record,
    mock_is_new_record,
    mock_get_historic_observations,
):
    ebird_api_key = "test_key"
    state_list = [{"comName": "SpeciesA"}]
    county = {"code": "CountyCodeA", "name": "CountyA"}
    day = date(2023, 10, 1)
    review_species = {"review_species": [], "county_groups": []}

    mock_get_historic_observations.return_value = [
        {"comName": "SpeciesB", "subId": "sub123"}
    ]
    mock_is_new_record.return_value = True
    mock_pelagic_record.return_value = False
    mock_observation_has_media.return_value = True

    result = _find_record_of_interest(
        ebird_api_key, "", state_list, county, day, review_species
    )

    assert len(result) == 1
    assert result[0]["observation"]["comName"] == "SpeciesB"
    assert result[0]["new"] is True
    assert result[0]["media"] is True
    mock_get_historic_observations.assert_called_once_with(
        token=ebird_api_key,
        area=county["code"],
        date=day,
        category="species",
        rank="create",
        detail="full",
    )
    mock_is_new_record.assert_called_once()
    mock_pelagic_record.assert_called_once()
    mock_observation_has_media.assert_called_once()


@patch("get_reports.get_records_to_review.get_historic_observations")
@patch("get_reports.get_records_to_review._is_new_record")
@patch("get_reports.get_records_to_review._pelagic_record")
@patch("get_reports.get_records_to_review._observation_has_media")
@patch("get_reports.get_records_to_review._reviewable_species")
@patch(
    "get_reports.get_records_to_review._reviewable_species_with_no_exclusions"
)
def test_find_record_of_interest_reviewable_species(
    mock_reviewable_species_with_no_exclusions,
    mock_reviewable_species,
    mock_observation_has_media,
    mock_pelagic_record,
    mock_is_new_record,
    mock_get_historic_observations,
):
    ebird_api_key = "test_key"
    state_list = [{"comName": "SpeciesA"}]
    county = {"code": "CountyCodeA", "name": "CountyA"}
    day = date(2023, 10, 1)
    review_species = {
        "review_species": [{"comName": "SpeciesB"}],
        "county_groups": [],
    }

    mock_get_historic_observations.return_value = [
        {"comName": "SpeciesB", "subId": "sub123"}
    ]
    mock_is_new_record.return_value = False
    mock_reviewable_species.return_value = {"comName": "SpeciesB"}
    mock_reviewable_species_with_no_exclusions.return_value = True
    mock_pelagic_record.return_value = False
    mock_observation_has_media.return_value = True

    result = _find_record_of_interest(
        ebird_api_key, "", state_list, county, day, review_species
    )

    assert len(result) == 1
    assert result[0]["observation"]["comName"] == "SpeciesB"
    assert result[0]["new"] is False
    assert result[0]["reviewable"] is True
    assert result[0]["review_species"]["comName"] == "SpeciesB"
    assert result[0]["media"] is True
    mock_get_historic_observations.assert_called_once_with(
        token=ebird_api_key,
        area=county["code"],
        date=day,
        category="species",
        rank="create",
        detail="full",
    )
    mock_is_new_record.assert_called_once()
    mock_reviewable_species.assert_called_once()
    mock_reviewable_species_with_no_exclusions.assert_called_once()
    mock_pelagic_record.assert_called_once()
    mock_observation_has_media.assert_called_once()


@patch("get_reports.get_records_to_review.get_historic_observations")
@patch("get_reports.get_records_to_review._is_new_record")
@patch("get_reports.get_records_to_review._pelagic_record")
@patch("get_reports.get_records_to_review._reviewable_species")
def test_find_record_of_interest_no_records(
    mock_reviewable_species,
    mock_pelagic_record,
    mock_is_new_record,
    mock_get_historic_observations,
):
    ebird_api_key = "test_key"
    state_list = [{"comName": "SpeciesA"}]
    county = {"code": "CountyCodeA", "name": "CountyA"}
    day = date(2023, 10, 1)
    review_species = {"review_species": [], "county_groups": []}

    mock_get_historic_observations.return_value = []
    mock_is_new_record.return_value = False
    mock_reviewable_species.return_value = None

    result = _find_record_of_interest(
        ebird_api_key, "", state_list, county, day, review_species
    )

    assert len(result) == 0
    mock_get_historic_observations.assert_called_once_with(
        token=ebird_api_key,
        area=county["code"],
        date=day,
        category="species",
        rank="create",
        detail="full",
    )
    mock_is_new_record.assert_not_called()
    mock_reviewable_species.assert_not_called()
    mock_pelagic_record.assert_not_called()


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


class MockContinuationRecord:
    def __init__(self, initial_list) -> None:
        self._to_review = initial_list
        return

    def records(self) -> list:
        return []

    def counties(self) -> list:
        return self._to_review

    def complete(self) -> None:
        return

    def update(self, county: dict, review_records: list) -> None:
        return


@patch("get_reports.get_records_to_review._iterate_days_in_month")
@patch("get_reports.get_records_to_review._find_record_of_interest")
@patch(
    "get_reports.get_records_to_review.continuation_record.ContinuationRecord",
    new=MockContinuationRecord,
)
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
        ebird_api_key, "", state_list, counties, year, month, day, review_species
    )

    assert len(result) == 1
    assert result[0]["county"] == "CountyA"
    assert len(result[0]["records"]) == 1
    assert result[0]["records"][0]["observation"]["comName"] == "SpeciesB"
    assert result[0]["records"][0]["new"] is True

@patch("get_reports.get_records_to_review._iterate_days_in_month")
@patch("get_reports.get_records_to_review._find_record_of_interest")
@patch(
    "get_reports.get_records_to_review.continuation_record.ContinuationRecord",
    new=MockContinuationRecord,
)
def test_get_records_to_review_single_county_all_year(
    mock_find_record_of_interest, mock_iterate_days_in_month
):
    ebird_api_key = "test_key"
    state_list = [{"comName": "SpeciesA"}]
    counties = [{"name": "CountyA", "code": "CountyCodeA"}]
    year = 2023
    month = 0
    day = 1
    review_species = {"review_species": [], "county_groups": []}

    mock_iterate_days_in_month.return_value = [date(year, 1, 1)]
    mock_find_record_of_interest.return_value = [
        {"observation": {"comName": "SpeciesB"}, "new": True}
    ]

    result = get_records_to_review(
        ebird_api_key,
        "",
        state_list,
        counties,
        year,
        month,
        day,
        review_species,
    )

    assert len(result) == 1
    assert result[0]["county"] == "CountyA"
    assert len(result[0]["records"]) == 12
    assert result[0]["records"][0]["observation"]["comName"] == "SpeciesB"
    assert result[0]["records"][0]["new"] is True

@patch("get_reports.get_records_to_review._iterate_days_in_month")
@patch("get_reports.get_records_to_review._find_record_of_interest")
@patch(
    "get_reports.get_records_to_review.continuation_record.ContinuationRecord",
    new=MockContinuationRecord,
)
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
        ebird_api_key,
        "",
        state_list,
        counties,
        year,
        month,
        day,
        review_species,
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
@patch(
    "get_reports.get_records_to_review.continuation_record.ContinuationRecord",
    new=MockContinuationRecord,
)
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
        ebird_api_key,
        "",
        state_list,
        counties,
        year,
        month,
        day,
        review_species,
    )

    assert len(result) == 0


@patch("get_reports.get_records_to_review._iterate_days_in_month")
@patch("get_reports.get_records_to_review._find_record_of_interest")
@patch(
    "get_reports.get_records_to_review.continuation_record.ContinuationRecord",
    new=MockContinuationRecord,
)
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
        ebird_api_key,
        "",
        state_list,
        counties,
        year,
        month,
        day,
        review_species,
    )

    assert len(result) == 1
    assert result[0]["county"] == "CountyA"
    assert len(result[0]["records"]) == 2
    assert result[0]["records"][0]["observation"]["comName"] == "SpeciesB"
    assert result[0]["records"][0]["new"] is True
    assert result[0]["records"][1]["observation"]["comName"] == "SpeciesC"
    assert result[0]["records"][1]["new"] is False


@patch("get_reports.get_records_to_review.get_checklist")
def test_pelagic_record_true(mock_get_checklist):
    ebird_api_key = "test_key"
    observation = {"subnational2Name": "PelagicCounty", "subId": "sub123"}
    pelagic_counties = ["PelagicCounty"]
    mock_get_checklist.return_value = {"protocolId": "P60"}

    result = _pelagic_record(ebird_api_key, "", observation, pelagic_counties)

    assert result is True
    mock_get_checklist.assert_called_once_with(
        token=ebird_api_key, sub_id="sub123"
    )


@patch("get_reports.get_records_to_review.get_checklist")
def test_pelagic_record_false_not_pelagic_county(mock_get_checklist):
    ebird_api_key = "test_key"
    observation = {"subnational2Name": "NonPelagicCounty", "subId": "sub123"}
    pelagic_counties = ["PelagicCounty"]

    result = _pelagic_record(ebird_api_key, "", observation, pelagic_counties)

    assert result is False
    mock_get_checklist.assert_not_called()


@patch("get_reports.get_records_to_review.get_checklist")
def test_pelagic_record_false_wrong_protocol(mock_get_checklist):
    ebird_api_key = "test_key"
    observation = {"subnational2Name": "PelagicCounty", "subId": "sub123"}
    pelagic_counties = ["PelagicCounty"]
    mock_get_checklist.return_value = {"protocolId": "P50"}

    result = _pelagic_record(ebird_api_key, "", observation, pelagic_counties)

    assert result is False
    mock_get_checklist.assert_called_once_with(
        token=ebird_api_key, sub_id="sub123"
    )


@patch("get_reports.get_records_to_review.get_checklist")
def test_pelagic_record_false_no_protocol(mock_get_checklist):
    ebird_api_key = "test_key"
    observation = {"subnational2Name": "PelagicCounty", "subId": "sub123"}
    pelagic_counties = ["PelagicCounty"]
    mock_get_checklist.return_value = {}

    result = _pelagic_record(ebird_api_key, "", observation, pelagic_counties)

    assert result is False
    mock_get_checklist.assert_called_once_with(
        token=ebird_api_key, sub_id="sub123"
    )


@patch("get_reports.get_records_to_review.get_checklist")
def test_observation_has_media_true(mock_get_checklist):
    ebird_api_key = "test_key"
    observation = {"subId": "sub123", "speciesCode": "speciesA"}
    mock_get_checklist.return_value = {
        "obs": [
            {"speciesCode": "speciesA", "mediaCounts": {"photos": 1}},
            {"speciesCode": "speciesB", "mediaCounts": {}},
        ]
    }

    result = _observation_has_media(ebird_api_key, "", observation)

    assert result is True
    mock_get_checklist.assert_called_once_with(
        token=ebird_api_key, sub_id="sub123"
    )


@patch("get_reports.get_records_to_review.get_checklist")
def test_observation_has_media_false_no_media(mock_get_checklist):
    ebird_api_key = "test_key"
    observation = {"subId": "sub123", "speciesCode": "speciesA"}
    mock_get_checklist.return_value = {
        "obs": [
            {"speciesCode": "speciesA", "mediaCounts": {}},
            {"speciesCode": "speciesB", "mediaCounts": {}},
        ]
    }

    result = _observation_has_media(ebird_api_key, "", observation)

    assert result is False
    mock_get_checklist.assert_called_once_with(
        token=ebird_api_key, sub_id="sub123"
    )


@patch("get_reports.get_records_to_review.get_checklist")
def test_observation_has_media_false_no_matching_species(mock_get_checklist):
    ebird_api_key = "test_key"
    observation = {"subId": "sub123", "speciesCode": "speciesC"}
    mock_get_checklist.return_value = {
        "obs": [
            {"speciesCode": "speciesA", "mediaCounts": {"photos": 1}},
            {"speciesCode": "speciesB", "mediaCounts": {"videos": 1}},
        ]
    }

    result = _observation_has_media(ebird_api_key, "", observation)

    assert result is False
    mock_get_checklist.assert_called_once_with(
        token=ebird_api_key, sub_id="sub123"
    )


@patch("get_reports.get_records_to_review.get_checklist")
def test_observation_has_media_false_empty_checklist(mock_get_checklist):
    ebird_api_key = "test_key"
    observation = {"subId": "sub123", "speciesCode": "speciesA"}
    mock_get_checklist.return_value = {"obs": []}

    result = _observation_has_media(ebird_api_key, "", observation)

    assert result is False
    mock_get_checklist.assert_called_once_with(
        token=ebird_api_key, sub_id="sub123"
    )


@patch("get_reports.get_records_to_review.get_checklist")
def test__get_checklist_with_retry_success_first_attempt(mock_get_checklist):
    api_key = "test_key"
    observation = "sub123"
    mock_get_checklist.return_value = {"protocolId": "P22"}

    result = _get_checklist_with_retry(api_key, observation)

    assert result == {"protocolId": "P22"}
    mock_get_checklist.assert_called_once_with(
        token=api_key, sub_id=observation
    )


@patch("get_reports.get_records_to_review.sleep")
@patch("get_reports.get_records_to_review.get_checklist")
def test__get_checklist_with_retry_success_second_attempt(
    mock_get_checklist, mock_sleep
):
    api_key = "test_key"
    observation = "sub123"
    mock_get_checklist.side_effect = [
        OSError("Connection failed"),
        {"protocolId": "P22"},
    ]

    result = _get_checklist_with_retry(api_key, observation)

    assert result == {"protocolId": "P22"}
    assert mock_get_checklist.call_count == 2
    mock_sleep.assert_called_once_with(0.1)


@patch("get_reports.get_records_to_review.sleep")
@patch("get_reports.get_records_to_review.get_checklist")
def test__get_checklist_with_retry_success_third_attempt(
    mock_get_checklist, mock_sleep
):
    api_key = "test_key"
    observation = "sub123"
    mock_get_checklist.side_effect = [
        OSError("Connection failed"),
        OSError("Timeout"),
        {"protocolId": "P22"},
    ]

    result = _get_checklist_with_retry(api_key, observation)

    assert result == {"protocolId": "P22"}
    assert mock_get_checklist.call_count == 3
    assert mock_sleep.call_count == 2


@patch("get_reports.get_records_to_review.sleep")
@patch("get_reports.get_records_to_review.get_checklist")
def test__get_checklist_with_retry_all_attempts_fail(
    mock_get_checklist, mock_sleep
):
    api_key = "test_key"
    observation = "sub123"
    mock_get_checklist.side_effect = OSError("Connection failed")

    try:
        _get_checklist_with_retry(api_key, observation)
        assert False, "Expected OSError to be raised"
    except OSError:
        pass

    assert mock_get_checklist.call_count == 3
    assert mock_sleep.call_count == 3


@patch("get_reports.get_records_to_review.sleep")
@patch("get_reports.get_records_to_review.get_checklist")
def test__get_checklist_with_retry_sleep_progression(
    mock_get_checklist, mock_sleep
):
    api_key = "test_key"
    observation = "sub123"
    mock_get_checklist.side_effect = OSError("Connection failed")

    try:
        _get_checklist_with_retry(api_key, observation)
    except OSError:
        pass

    mock_sleep.assert_any_call(0.1)
    mock_sleep.assert_any_call(0.2)
    assert mock_sleep.call_count == 3
@patch("get_reports.get_records_to_review.sleep")
@patch("get_reports.get_records_to_review.get_historic_observations")
def test__get_historic_observations_with_retry_success_first_attempt(
    mock_get_historic_observations, mock_sleep
):
    token = "test_key"
    area = "US-VA"
    day = date(2023, 10, 1)
    category = "species"
    rank = "create"
    detail = "full"
    mock_get_historic_observations.return_value = [
        {"comName": "SpeciesA", "speciesCode": "speca"}
    ]

    result = _get_historic_observations_with_retry(
        token, area, day, category, rank, detail
    )

    assert result == [{"comName": "SpeciesA", "speciesCode": "speca"}]
    mock_get_historic_observations.assert_called_once_with(
        token=token,
        area=area,
        date=day,
        category=category,
        rank=rank,
        detail=detail,
    )
    mock_sleep.assert_not_called()


@patch("get_reports.get_records_to_review.sleep")
@patch("get_reports.get_records_to_review.get_historic_observations")
def test__get_historic_observations_with_retry_success_second_attempt(
    mock_get_historic_observations, mock_sleep
):
    token = "test_key"
    area = "US-VA"
    day = date(2023, 10, 1)
    category = "species"
    rank = "create"
    detail = "full"
    mock_get_historic_observations.side_effect = [
        OSError("Connection failed"),
        [{"comName": "SpeciesA", "speciesCode": "speca"}],
    ]

    result = _get_historic_observations_with_retry(
        token, area, day, category, rank, detail
    )

    assert result == [{"comName": "SpeciesA", "speciesCode": "speca"}]
    assert mock_get_historic_observations.call_count == 2
    mock_sleep.assert_called_once_with(0.1)


@patch("get_reports.get_records_to_review.sleep")
@patch("get_reports.get_records_to_review.get_historic_observations")
def test__get_historic_observations_with_retry_success_third_attempt(
    mock_get_historic_observations, mock_sleep
):
    token = "test_key"
    area = "US-VA"
    day = date(2023, 10, 1)
    category = "species"
    rank = "create"
    detail = "full"
    mock_get_historic_observations.side_effect = [
        OSError("Connection failed"),
        OSError("Timeout"),
        [{"comName": "SpeciesA", "speciesCode": "speca"}],
    ]

    result = _get_historic_observations_with_retry(
        token, area, day, category, rank, detail
    )

    assert result == [{"comName": "SpeciesA", "speciesCode": "speca"}]
    assert mock_get_historic_observations.call_count == 3
    assert mock_sleep.call_count == 2


@patch("get_reports.get_records_to_review.sleep")
@patch("get_reports.get_records_to_review.get_historic_observations")
def test__get_historic_observations_with_retry_all_attempts_fail(
    mock_get_historic_observations, mock_sleep
):
    token = "test_key"
    area = "US-VA"
    day = date(2023, 10, 1)
    category = "species"
    rank = "create"
    detail = "full"
    mock_get_historic_observations.side_effect = OSError("Connection failed")

    try:
        _get_historic_observations_with_retry(
            token, area, day, category, rank, detail
        )
        assert False, "Expected OSError to be raised"
    except OSError:
        pass

    assert mock_get_historic_observations.call_count == 3
    assert mock_sleep.call_count == 3


@patch("get_reports.get_records_to_review.sleep")
@patch("get_reports.get_records_to_review.get_historic_observations")
def test__get_historic_observations_with_retry_sleep_progression(
    mock_get_historic_observations, mock_sleep
):
    token = "test_key"
    area = "US-VA"
    day = date(2023, 10, 1)
    category = "species"
    rank = "create"
    detail = "full"
    mock_get_historic_observations.side_effect = OSError("Connection failed")

    try:
        _get_historic_observations_with_retry(
            token, area, day, category, rank, detail
        )
    except OSError:
        pass

    mock_sleep.assert_any_call(0.1)
    mock_sleep.assert_any_call(0.2)
    assert mock_sleep.call_count == 3
    @patch("get_reports.get_records_to_review._iterate_days_in_month")
    @patch("get_reports.get_records_to_review._find_record_of_interest")
    @patch(
        "get_reports.get_records_to_review.continuation_record.ContinuationRecord",
        new=MockContinuationRecord,
    )
    def test_get_records_to_review_multiple_months(
        mock_find_record_of_interest, mock_iterate_days_in_month
    ):
        ebird_api_key = "test_key"
        state_list = [{"comName": "SpeciesA"}]
        counties = [{"name": "CountyA", "code": "CountyCodeA"}]
        year = 2023
        month = 0  # All months
        day = 1
        review_species = {"review_species": [], "county_groups": []}

        mock_iterate_days_in_month.side_effect = [
            [date(2023, 1, 1)],
            [date(2023, 2, 1)],
            [date(2023, 3, 1)],
            [date(2023, 4, 1)],
            [date(2023, 5, 1)],
            [date(2023, 6, 1)],
            [date(2023, 7, 1)],
            [date(2023, 8, 1)],
            [date(2023, 9, 1)],
            [date(2023, 10, 1)],
            [date(2023, 11, 1)],
            [date(2023, 12, 1)],
        ]
        mock_find_record_of_interest.return_value = [
            {"observation": {"comName": "SpeciesB"}, "new": True}
        ]

        result = get_records_to_review(
            ebird_api_key, "", state_list, counties, year, month, day, review_species
        )

        assert len(result) == 1
        assert result[0]["county"] == "CountyA"
        assert len(result[0]["records"]) == 12
        assert mock_find_record_of_interest.call_count == 12




