import json
import logging
import os

def _check_counties_in_groups(county_list, review_species):
    """
    Checks the presence of counties in specified county groups and logs warnings
    if a county is not found in any group or is found in multiple groups.
    Args:
        county_list (list): A list of dictionaries, where each dictionary
            represents a county with at least a "name" key.
        review_species (dict): A dictionary containing information about species,
            including an optional "county_groups" key, which is a list of groups.
            Each group is a dictionary with a "counties" key that lists county
            names.
    Logs:
        - A warning if a county is not found in any county group.
        - A warning if a county is found in multiple county groups.
    """
    county_group_count = {county["name"]: 0 for county in county_list}
    for county in county_list:
        for group in review_species.get("county_groups", []):
            if county["name"] in group["counties"]:
                county_group_count[county["name"]] += 1

    for county, count in county_group_count.items():
        if count == 0:
            logging.warning("County %s not found in any county group", county)
        elif count > 1:
            logging.warning(
                "County %s found in multiple county groups", county
            )


def _check_species_in_taxonomy(review_species, taxonomy):
    """
    Checks if the species in the review list are present in the provided eBird
    taxonomy.
    Logs an informational message at the start of the check. For each species
    in the review list, it verifies whether the species' common name matches
    any common name in the taxonomy. If a species is not found in the taxonomy,
    a warning is logged.

    Args:
        review_species (dict): A dictionary containing a list of species under
            the key "review_species". Each species is expected to be a
            dictionary with a "comName" key.
        taxonomy (list): A list of dictionaries representing the eBird
            taxonomy. Each dictionary is expected to have a "comName" key.

    Logs:
        info: Indicates the start of the species check process.
        warning: Indicates that a species from the review list is not found in
            the taxonomy.
    """
    logging.info(
        "Checking species in state review list against eBird taxonomy."
    )
    for species in review_species["review_species"]:
        if not any(
            taxon["comName"] == species["comName"] for taxon in taxonomy
        ):
            logging.warning(
                "Species %s not found in eBird taxonomy", species["comName"]
            )


def _check_exclusions_in_counties(review_species, county_list, state):
    """
    Checks for exclusions in counties and logs warnings for any discrepancies.

    This function verifies that all counties listed in the `review_species`
    data structure are present in the provided `county_list`. Additionally,
    it checks that all exclusions specified in the `review_species` are
    either valid counties or valid county groups. If any discrepancies are
    found, warnings are logged.

    Args:
        review_species (dict): A dictionary containing information about
            county groups and species review data. Expected keys include:
            - "county_groups": A list of dictionaries, each containing a
              "counties" key with a list of county names.
            - "review_species": A list of dictionaries, each containing an
              optional "exclude" key with a list of exclusions.
        county_list (list): A list of dictionaries representing valid counties.
            Each dictionary should have a "name" key with the county name.
        state (str): The name of the state being processed, used for logging.

    Logs:
        - A warning if a county in `review_species["county_groups"]` is not
          found in `county_list`.
        - A warning if an exclusion in `review_species["review_species"]` is
          not found as a valid county or county group.
    """
    for group in review_species["county_groups"]:
        for county in group["counties"]:
            if not any(d["name"] == county for d in county_list):
                logging.warning(
                    "County %s not found in eBird list of counties for %s.",
                    county,
                    state,
                )
    for species in review_species["review_species"]:
        for exclusion in species.get("exclude", []):
            if not any(
                d["name"] == exclusion for d in county_list
            ) and not any(
                group["name"] == exclusion
                for group in review_species.get("county_groups", [])
            ):
                logging.warning(
                    "Exclusion %s was not found as a group or county",
                    exclusion,
                )


def get_review_rules(
    file_name: str, taxonomy: list, county_list: list, state: str
) -> dict:
    """
    Load and validate review rules from a JSON file.
    This function reads a JSON file containing review rules, validates the
    data against the provided taxonomy, county list, and state, and returns
    the parsed review rules as a dictionary.
    Args:
        file_name (str): The path to the JSON file containing review rules.
        taxonomy (list): A list of valid species or taxonomy to validate against.
        county_list (list): A list of counties to validate against.
        state (str): The state to validate exclusions against.
    Returns:
        dict: A dictionary containing the review rules if the file exists and
              passes validation. Returns an empty dictionary if the file does
              not exist or validation fails.
    Raises:
        json.JSONDecodeError: If the JSON file is not properly formatted.
        Any exceptions raised by the validation functions.
    Logging:
        Logs an error if the specified file does not exist.
    """
    if not os.path.exists(file_name):
        logging.error("File %s does not exist.", file_name)
        return {}
    with open(file_name, "rt", encoding="utf-8") as f:
        review_species = json.load(f)

    _check_counties_in_groups(county_list, review_species)
    _check_species_in_taxonomy(review_species, taxonomy)
    _check_exclusions_in_counties(review_species, county_list, state)

    return review_species
