# pylint: disable=W0613, W0212, C0116, C0114, C0115
from datetime import date
from unittest.mock import patch, mock_open
import pandas as pd

from get_reports.ebird_data_access import (
    get_checklist_with_retry,
    get_historic_observations_with_retry,
    read_database,
    get_historic_observations_from_database
)


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


@patch("get_reports.ebird_data_access.get_checklist")
def test_get_checklist_with_retry_success_first_attempt(mock_get_checklist):
    api_key = "test_key"
    observation = "sub123"
    mock_get_checklist.return_value = {"protocolId": "P22"}

    result = get_checklist_with_retry(api_key, observation)

    assert result == {"protocolId": "P22"}
    mock_get_checklist.assert_called_once_with(
        token=api_key, sub_id=observation
    )


@patch("get_reports.ebird_data_access.sleep")
@patch("get_reports.ebird_data_access.get_checklist")
def test_get_checklist_with_retry_success_second_attempt(
    mock_get_checklist, mock_sleep
):
    api_key = "test_key"
    observation = "sub123"
    mock_get_checklist.side_effect = [
        OSError("Connection failed"),
        {"protocolId": "P22"},
    ]

    result = get_checklist_with_retry(api_key, observation)

    assert result == {"protocolId": "P22"}
    assert mock_get_checklist.call_count == 2
    mock_sleep.assert_called_once_with(0.1)


@patch("get_reports.ebird_data_access.sleep")
@patch("get_reports.ebird_data_access.get_checklist")
def test_get_checklist_with_retry_success_third_attempt(
    mock_get_checklist, mock_sleep
):
    api_key = "test_key"
    observation = "sub123"
    mock_get_checklist.side_effect = [
        OSError("Connection failed"),
        OSError("Timeout"),
        {"protocolId": "P22"},
    ]

    result = get_checklist_with_retry(api_key, observation)

    assert result == {"protocolId": "P22"}
    assert mock_get_checklist.call_count == 3
    assert mock_sleep.call_count == 2


@patch("get_reports.ebird_data_access.sleep")
@patch("get_reports.ebird_data_access.get_checklist")
def test_get_checklist_with_retry_all_attempts_fail(
    mock_get_checklist, mock_sleep
):
    api_key = "test_key"
    observation = "sub123"
    mock_get_checklist.side_effect = OSError("Connection failed")

    try:
        get_checklist_with_retry(api_key, observation)
        assert False, "Expected OSError to be raised"
    except OSError:
        pass

    assert mock_get_checklist.call_count == 3
    assert mock_sleep.call_count == 3


@patch("get_reports.ebird_data_access.sleep")
@patch("get_reports.ebird_data_access.get_checklist")
def test_get_checklist_with_retry_sleep_progression(
    mock_get_checklist, mock_sleep
):
    api_key = "test_key"
    observation = "sub123"
    mock_get_checklist.side_effect = OSError("Connection failed")

    try:
        get_checklist_with_retry(api_key, observation)
    except OSError:
        pass

    mock_sleep.assert_any_call(0.1)
    mock_sleep.assert_any_call(0.2)
    assert mock_sleep.call_count == 3


@patch("get_reports.ebird_data_access.sleep")
@patch("get_reports.ebird_data_access.get_historic_observations")
def test_get_historic_observations_with_retry_success_first_attempt(
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

    result = get_historic_observations_with_retry(
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


@patch("get_reports.ebird_data_access.sleep")
@patch("get_reports.ebird_data_access.get_historic_observations")
def test_get_historic_observations_with_retry_success_second_attempt(
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

    result = get_historic_observations_with_retry(
        token, area, day, category, rank, detail
    )

    assert result == [{"comName": "SpeciesA", "speciesCode": "speca"}]
    assert mock_get_historic_observations.call_count == 2
    mock_sleep.assert_called_once_with(0.1)


@patch("get_reports.ebird_data_access.sleep")
@patch("get_reports.ebird_data_access.get_historic_observations")
def test_get_historic_observations_with_retry_success_third_attempt(
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

    result = get_historic_observations_with_retry(
        token, area, day, category, rank, detail
    )

    assert result == [{"comName": "SpeciesA", "speciesCode": "speca"}]
    assert mock_get_historic_observations.call_count == 3
    assert mock_sleep.call_count == 2


@patch("get_reports.ebird_data_access.sleep")
@patch("get_reports.ebird_data_access.get_historic_observations")
def test_get_historic_observations_with_retry_all_attempts_fail(
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
        get_historic_observations_with_retry(
            token, area, day, category, rank, detail
        )
        assert False, "Expected OSError to be raised"
    except OSError:
        pass

    assert mock_get_historic_observations.call_count == 3
    assert mock_sleep.call_count == 3


@patch("get_reports.ebird_data_access.sleep")
@patch("get_reports.ebird_data_access.get_historic_observations")
def test_get_historic_observations_with_retry_sleep_progression(
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
        get_historic_observations_with_retry(
            token, area, day, category, rank, detail
        )
    except OSError:
        pass

    mock_sleep.assert_any_call(0.1)
    mock_sleep.assert_any_call(0.2)
    assert mock_sleep.call_count == 3


@patch("builtins.open", new_callable=mock_open, read_data="data")
@patch("pandas.read_csv")
def test_read_database_success(mock_read_csv, mock_open_function):
    mock_read_csv.return_value = pd.DataFrame(
        {
            3: ["category1"],
            5: ["SpeciesA"],
            10: [1],
            19: ["subnational2Name"],
            20: ["county"],
            30: ["obsDt"],
            31: ["obsTime"],
            34: ["subId"],
            37: ["protocolId"],
            46: ["media"],
            47: ["approved"],
        }
    )

    result = read_database("dummy_file.csv")

    assert result == [
        {
            "category": "category1",
            "comName": "SpeciesA",
            "howMany": 1,
            "subnational2Name": "subnational2Name",
            "county": "county",
            "obsDt": "obsDt obsTime",
            "obsTime": "obsTime",
            "subId": "subId",
            "protocolId": "protocolId",
            "media": "media",
            "approved": "approved",
        }
    ]
    mock_read_csv.assert_called_once_with(
        "dummy_file.csv",
        dtype={"24": str},
        usecols=[3, 5, 10, 19, 20, 30, 31, 34, 37, 46, 47],
    )


@patch("builtins.open", new_callable=mock_open)
@patch("pandas.read_csv")
def test_read_database_file_not_found(mock_read_csv, mock_open_function):
    mock_read_csv.side_effect = FileNotFoundError
    result = read_database("non_existent_file.csv")

    assert result == []


@patch("builtins.open", new_callable=mock_open)
@patch("pandas.read_csv")
def test_read_database_os_error(mock_read_csv, mock_open_function):
    mock_read_csv.side_effect = OSError("Read error")

    result = read_database("dummy_file.csv")

    assert result == []
    mock_read_csv.assert_called_once_with(
        "dummy_file.csv",
        dtype={"24": str},
        usecols=[3, 5, 10, 19, 20, 30, 31, 34, 37, 46, 47],
    )
@patch("get_reports.ebird_data_access.get_historic_observations_from_database")
def test_get_historic_observations_from_database_single_match(mock_function):

    database = [
        {
            "county": "Fairfax",
            "category": "species",
            "obsDt": "2023-10-01 14:30:00",
            "comName": "SpeciesA",
        },
        {
            "county": "Loudoun",
            "category": "species",
            "obsDt": "2023-10-01 10:00:00",
            "comName": "SpeciesB",
        },
    ]

    result = get_historic_observations_from_database(
        database, area="Fairfax", day=date(2023, 10, 1), category="species"
    )

    assert len(result) == 1
    assert result[0]["county"] == "Fairfax"
    assert result[0]["comName"] == "SpeciesA"


def test_get_historic_observations_from_database_multiple_matches():

    database = [
        {
            "county": "Fairfax",
            "category": "species",
            "obsDt": "2023-10-01 14:30:00",
            "comName": "SpeciesA",
        },
        {
            "county": "Fairfax",
            "category": "species",
            "obsDt": "2023-10-01 10:00:00",
            "comName": "SpeciesB",
        },
    ]

    result = get_historic_observations_from_database(
        database, area="Fairfax", day=date(2023, 10, 1), category="species"
    )

    assert len(result) == 2


def test_get_historic_observations_from_database_no_matches():

    database = [
        {
            "county": "Fairfax",
            "category": "species",
            "obsDt": "2023-10-01 14:30:00",
            "comName": "SpeciesA",
        },
    ]

    result = get_historic_observations_from_database(
        database, area="Loudoun", day=date(2023, 10, 1), category="species"
    )

    assert result == []


def test_get_historic_observations_from_database_different_dates():

    database = [
        {
            "county": "Fairfax",
            "category": "species",
            "obsDt": "2023-10-01 14:30:00",
            "comName": "SpeciesA",
        },
        {
            "county": "Fairfax",
            "category": "species",
            "obsDt": "2023-10-02 10:00:00",
            "comName": "SpeciesB",
        },
    ]

    result = get_historic_observations_from_database(
        database, area="Fairfax", day=date(2023, 10, 1), category="species"
    )

    assert len(result) == 1
    assert result[0]["comName"] == "SpeciesA"


def test_get_historic_observations_from_database_empty_database():

    database = []

    result = get_historic_observations_from_database(
        database, area="Fairfax", day=date(2023, 10, 1), category="species"
    )

    assert result == []

