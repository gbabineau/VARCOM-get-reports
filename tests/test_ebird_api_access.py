# pylint: disable=W0613, W0212, C0116, C0114, C0115
from datetime import date
from unittest.mock import patch

from get_reports.ebird_api_access import (
    get_checklist_with_retry,
    get_historic_observations_with_retry,
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

@patch("get_reports.ebird_api_access.get_checklist")
def test_get_checklist_with_retry_success_first_attempt(mock_get_checklist):
    api_key = "test_key"
    observation = "sub123"
    mock_get_checklist.return_value = {"protocolId": "P22"}

    result = get_checklist_with_retry(api_key, observation)

    assert result == {"protocolId": "P22"}
    mock_get_checklist.assert_called_once_with(
        token=api_key, sub_id=observation
    )


@patch("get_reports.ebird_api_access.sleep")
@patch("get_reports.ebird_api_access.get_checklist")
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


@patch("get_reports.ebird_api_access.sleep")
@patch("get_reports.ebird_api_access.get_checklist")
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


@patch("get_reports.ebird_api_access.sleep")
@patch("get_reports.ebird_api_access.get_checklist")
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


@patch("get_reports.ebird_api_access.sleep")
@patch("get_reports.ebird_api_access.get_checklist")
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


@patch("get_reports.ebird_api_access.sleep")
@patch("get_reports.ebird_api_access.get_historic_observations")
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


@patch("get_reports.ebird_api_access.sleep")
@patch("get_reports.ebird_api_access.get_historic_observations")
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


@patch("get_reports.ebird_api_access.sleep")
@patch("get_reports.ebird_api_access.get_historic_observations")
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


@patch("get_reports.ebird_api_access.sleep")
@patch("get_reports.ebird_api_access.get_historic_observations")
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


@patch("get_reports.ebird_api_access.sleep")
@patch("get_reports.ebird_api_access.get_historic_observations")
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


