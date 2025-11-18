import logging
from calendar import monthrange
from datetime import date

from ebird.api import get_historic_observations, get_checklist
from time import sleep
from get_reports import (
    continuation_record,
    )

def get_checklist_with_retry(api_key: str, observation: str) -> list:
    attempts = 0
    while attempts < 3:
        try:
            return get_checklist(token=api_key, sub_id=observation)
        except OSError as exc:
            attempts += 1
            sleep(0.1 * attempts)
            logging.warning(
                "get_checklist attempt %d failed for args %s, %s",
                attempts,
                observation,
                exc,
            )
            if attempts >= 3:
                logging.error(
                    "get_checklist failed after %d attempts for args %s, %s",
                    attempts,
                    observation,
                    exc,
                )
                raise

def get_historic_observations_with_retry(
    token: str,
    area:str,
    day: date,
    category:str,
    rank:str,
    detail:str,
) -> list:
    attempts = 0
    while attempts < 3:
        try:
            return get_historic_observations(token=token, area=area, date=day, category=category, rank=rank, detail=detail)
        except OSError as exc:
            attempts += 1
            sleep(0.1 * attempts)
            logging.warning(
                "get_historic_observations attempt %d failed for args %s, %s, %s, %s, %s, %s",
                attempts,
                area,
                day,
                category,
                rank,
                detail,
                exc,
            )
            if attempts >= 3:
                logging.error(
                    "get_checklist failed after %d attempts for args %s, %s, %s, %s, %s, %s",
                    attempts,
                    area,
                    day,
                    category,
                    rank,
                    detail,
                    exc
                )
                raise

def _county_in_list_or_group(
    county_name: str, exclusion_list: list, county_groups: list
) -> bool:
    """
    Determines if a given county is included in an exclusion list or within a group of counties.

    Args:
        county_name (str): The name of the county to check.
        exclusion_list (list): A list of county names to exclude.
        county_groups (list): A list of dictionaries representing county groups.
                                Each dictionary should have a "name" key for the group name
                                and a "counties" key containing a list of county names in the group.

    Returns:
        bool: True if the county is in the exclusion list or in a group specified by the exclusion list,
                False otherwise.
    """
    included = False
    if county_name in exclusion_list:
        included = True
    else:
        for exclusion in exclusion_list:
            groups = county_groups
            group = next((g for g in groups if g["name"] == exclusion), None)
            if group and county_name in group["counties"]:
                included = True
    return included


def _is_new_record(observation: dict, state_list: list) -> bool:
    """
    Determines if a given observation is a new record based on its exotic category
    and whether its common name is already present in the state list.

    Args:
        observation (dict): A dictionary containing details of the observation.
            Expected to have at least the key "exoticCategory" (str) and "comName" (str).
        state_list (list): A list of dictionaries, each representing a species in the state.
            Each dictionary is expected to have the key "comName" (str).

    Returns:
        bool: True if the observation is a new record (i.e., its "exoticCategory" is not "X"
              and its "comName" is not found in the state list), otherwise False.
    """
    return observation.get("exoticCategory", "") != "X" and not any(
        species["comName"] == observation["comName"] for species in state_list
    )


def _reviewable_species(observation: dict, species_to_review: list) -> bool:
    """
    Determines if a given observation corresponds to a species in the review list.

    Args:
        observation (dict): A dictionary representing an observation, expected to contain a "comName" key.
        species_to_review (list): A list of dictionaries, where each dictionary represents a species
                                  and is expected to contain a "comName" key.

    Returns:
        bool: True if the observation's "comName" matches the "comName" of any species in the review list,
              otherwise False.
    """
    return next(
        (
            species
            for species in species_to_review
            if species["comName"] == observation["comName"]
        ),
        None,
    )


def _reviewable_species_with_no_exclusions(
    matching_species: dict, review_species: dict, county: dict
) -> bool:
    """
    Determines if a species is reviewable based on matching criteria and exclusions.

    Args:
        matching_species (dict): A dictionary containing species matching criteria.
            Keys may include "only" (list of counties where the species is reviewable)
            and "exclude" (list of counties where the species is not reviewable).
        review_species (dict): A dictionary containing additional review criteria,
            including "county_groups" (list of grouped counties for matching purposes).
        county (dict): A dictionary representing the county information, including
            the "name" key for the county's name.

    Returns:
        bool: True if the species is reviewable in the given county, False otherwise.
    """
    only_match = matching_species.get("only", [])
    if only_match:
        reviewable = _county_in_list_or_group(
            county["name"], only_match, review_species.get("county_groups", [])
        )
    elif _county_in_list_or_group(
        county["name"],
        matching_species.get("exclude", []),
        review_species.get("county_groups", []),
    ):
        reviewable = False
    else:
        reviewable = True
    return reviewable


def _pelagic_record(
    ebird_api_key: str, observation: dict, pelagic_counties: list
) -> bool:
    """
    Determines if a given observation is a pelagic record.

    A pelagic record is identified if the observation's county is in the list of pelagic counties
    and the associated checklist uses the pelagic protocol (protocol ID 'P60').

    Args:
        ebird_api_key (str): The API key for accessing eBird data.
        observation (dict): A dictionary containing observation details, including 'subnational2Name'
                            (county name) and 'subId' (checklist ID).
        pelagic_counties (list): A list of county names considered pelagic.

    Returns:
        bool: True if the observation is a pelagic record, False otherwise.
    """
    if observation["subnational2Name"] in pelagic_counties:
        # get checklist and see if it uses the pelagic protocol
        checklist = get_checklist_with_retry(ebird_api_key, observation=observation["subId"])
        return checklist.get("protocolId", "") == "P60"
    else:
        return False


def _observation_has_media(ebird_api_key: str, observation: dict) -> bool:
    """
    Determines if an observation has associated media (photos, videos, etc.).

    Args:
        observation (dict): A dictionary representing an observation.

    Returns:
        bool: True if the observation has associated media, False otherwise.
    """
    checklist = get_checklist_with_retry(ebird_api_key, observation=observation["subId"])
    return any(
        obs.get("speciesCode") == observation["speciesCode"]
        and obs.get("mediaCounts")
        for obs in checklist.get("obs", [])
    )


def _find_record_of_interest(
    ebird_api_key: str,
    state_list: list,
    county: dict,
    day: date,
    review_species: dict,
) -> list:
    """
    Identifies records of interest from historic bird observations based on
    specified criteria such as new species, reviewable species, and exclusions.

    Args:
        ebird_api_key (str): The API key for accessing eBird data.
        state_list (list): A list of species already recorded in the state.
        county (dict): A dictionary containing county information, including
            "code" (county identifier) and "name" (county name).
        day (date): The date for which observations are being retrieved.
        review_species (dict): A dictionary containing reviewable species
            information, including "review_species" (list of species to review)
            and any exclusion criteria.

    Returns:
        list: A list of dictionaries representing records of interest. Each
        dictionary may include:
            - "observation" (dict): The observation data.
            - "new" (bool): Whether the species is new to the state list.
            - "reviewable" (bool, optional): Whether the species is reviewable.
            - "review_species" (list, optional): Matching reviewable species.
    """

    observations = get_historic_observations_with_retry(
        token=ebird_api_key,
        area=county["code"],
        day=day,
        category="species",
        rank="create",
        detail="full",
    )
    pelagic_counties = next(
        (
            group["counties"]
            for group in review_species.get("county_groups", [])
            if group["name"] == "Pelagic Counties"
        ),
        [],
    )
    records_of_interest = []
    for observation in observations:
        if _is_new_record(observation, state_list):
            if not _pelagic_record(
                ebird_api_key=ebird_api_key,
                observation=observation,
                pelagic_counties=pelagic_counties,
            ):
                logging.info(
                    "Species %s not in state list. A new record?",
                    observation["comName"],
                )
                records_of_interest.append(
                    {
                        "observation": observation,
                        "new": True,
                        "media": _observation_has_media(
                            ebird_api_key=ebird_api_key,
                            observation=observation,
                        ),
                    }
                )
        elif matching_species := _reviewable_species(
            observation, review_species["review_species"]
        ):
            if _reviewable_species_with_no_exclusions(
                matching_species, review_species, county
            ) and not _pelagic_record(
                ebird_api_key=ebird_api_key,
                observation=observation,
                pelagic_counties=pelagic_counties,
            ):
                logging.info(
                    "Species %s is reviewable in %s.",
                    observation["comName"],
                    county["name"],
                )
                records_of_interest.append(
                    {
                        "observation": observation,
                        "new": False,
                        "reviewable": True,
                        "review_species": matching_species,
                        "media": _observation_has_media(
                            ebird_api_key=ebird_api_key,
                            observation=observation,
                        ),
                    }
                )
    return records_of_interest


def _iterate_days_in_month(year: int, month: int, day):
    """
    Generate an iterator over all the days in a given month of a specific year.

    Args:
        year (int): The year for which the days are to be generated.
        month (int): The month (1-12) for which the days are to be generated.

    Yields:
        datetime.date: A date object for each day in the specified month.

    Example:
        for day in _iterate_days_in_month(2023, 2):
            print(day)
        # Output: 2023-02-01, 2023-02-02, ..., 2023-02-28
    """
    if day == 0:
        num_days = monthrange(year, month)[1]
        for day_of_month in range(1, num_days + 1):
            yield date(year, month, day_of_month)
    else:
        yield date(year, month, day)



def get_records_to_review(
    ebird_api_key: str,
    state_list: list,
    counties: list,
    year: int,
    month: int,
    day: int,
    review_species: dict,
) -> list:
    """
    Retrieves a list of bird observation records that require review for a given
    set of counties, state(s), and a specific month and year.

    Args:
        ebird_api_key (str): The API key for accessing eBird data.
        state_list (list): A list of state abbreviations to filter the records.
        counties (list): A list of dictionaries representing counties, where each
            dictionary contains at least a "name" key.
        year (int): The year for which to retrieve records.
        month (int): The month for which to retrieve records (1-12).
        review_species (dict): A dictionary of species to review, where keys are
            species names and values are additional filtering criteria.

    Returns:
        list: A list of dictionaries, where each dictionary contains:
            - "county" (str): The name of the county.
            - "records" (list): A list of records for the county that match the
              review criteria.
    """
    continuation = continuation_record.ContinuationRecord(counties)
    records_to_review = continuation.records()
    for county in continuation.counties():
        county_records = []
        if month == 0:
            month_range = range(1, 13)
        else:
            month_range = range(month, month+1)

        for month_in_year in month_range:
            for day_in_month in _iterate_days_in_month(year, month_in_year, day):
                records_for_county = _find_record_of_interest(
                    ebird_api_key, state_list, county, day_in_month, review_species
                )
                if records_for_county:
                    county_records.extend(records_for_county)
        if county_records:
            records_to_review.append(
                {"county": county["name"], "records": county_records}
            )
        continuation.update(county, records_to_review)
    continuation.complete()
    return records_to_review
