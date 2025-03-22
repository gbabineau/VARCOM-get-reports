""" """

import argparse
import json
import logging
import os
import sys
from dateutil import parser
from datetime import date

from ebird.api import get_historic_observations, get_regions
from get_reports import get_taxonomy

ebird_api_key_name = "EBIRDAPIKEY"


def check_counties_in_groups(county_list, review_species):
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


def check_species_in_taxonomy(review_species, taxonomy):
    for species in review_species["review_species"]:
        if not any(
            taxon["comName"] == species["comName"] for taxon in taxonomy
        ):
            logging.warning(
                "Species %s not found in eBird taxonomy", species["comName"]
            )


def check_exclusions_in_counties(review_species, county_list, state):
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


def get_review_species(
    file_name: str, taxonomy: list, county_list: list, state: str
) -> dict:
    """
    Retrieves the list of review species from a file.

    Args:
        file (str): The file containing the review species.
        taxonomy (list): The taxonomy list.

    Returns:
        list: A dict containing information about the of review species.
    """
    if not os.path.exists(file_name):
        logging.error("File %s does not exist.", file_name)
        return {}
    with open(file_name, "rt", encoding="utf-8") as f:
        review_species = json.load(f)

    check_counties_in_groups(county_list, review_species)
    check_species_in_taxonomy(review_species, taxonomy)
    check_exclusions_in_counties(review_species, county_list, state)

    return review_species


def get_state_list(file_name: str, taxonomy: list) -> dict:
    """
    Retrieves the list of states from a file.

    Args:
        file (str): The file containing the states.

    Returns:
        list: A dict containing information about the states.
    """
    if not os.path.exists(file_name):
        logging.error("File %s does not exist.", file_name)
        return {}
    with open(file_name, "rt", encoding="utf-8") as f:
        state_list = json.load(f)["state_list"]
    for species in state_list:
        if not any(
            taxon["comName"] == species["comName"] for taxon in taxonomy
        ):
            logging.warning(
                "Species %s not found in eBird taxonomy", species["comName"]
            )

    return state_list


def parse_arguments() -> argparse.Namespace:
    """Parse the command line arguments."""
    arg_parser = argparse.ArgumentParser(
        prog="get_reports", description="Get eBird reports of interest."
    )
    arg_parser.add_argument(
        "--review_species_file",
        help="Species requiring review",
        default="get_reports/data/varcom_review_species.json",
    )
    arg_parser.add_argument("--state", help="State to review", default="US-VA")
    arg_parser.add_argument(
        "--version", action="version", version="%(prog)s 0.0.0"
    )
    arg_parser.add_argument(
        "--verbose", action="store_true", help="increase verbosity"
    )
    return arg_parser.parse_args()


def find_record_of_interest(
    ebird_api_key: str,
    state_list: list,
    county: str,
    day: date,
    review_species: dict,
) -> list:
    """Find records of interest for a county and date."""
    observations = get_historic_observations(
        token=ebird_api_key, area=county, date=day, category="species"
    )
    records_of_interest = []
    for observation in observations:
        if not any(
            species["comName"] == observation["comName"]
            for species in state_list
        ):
            logging.info(
                "Species %s not in state list. A new record?",
                observation["comName"],
            )
            records_of_interest.append(
                {"observation": observation, "new": True}
            )
        else:
            matching_species = next(
                (
                    species
                    for species in review_species["review_species"]
                    if species["comName"] == observation["comName"]
                ),
                None,
            )
            if matching_species:
                logging.info(
                    "Species %s is reviewable in %s.",
                    observation["comName"],
                    county,
                )
                records_of_interest.append(
                    {
                        "observation": observation,
                        "new": False,
                        "reviewable": True,
                        "review_species": matching_species,
                    }
                )
                break
    return records_of_interest


def write_taxonomy_to_file(taxonomy: list, file_name: str) -> None:
    """
    Writes the taxonomy to a file.

    Args:
        taxonomy (list): The taxonomy list.
        file_name (str): The file to write the taxonomy to.
    """
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(taxonomy, f, ensure_ascii=False, indent=4)
    logging.info("Taxonomy written to %s", file_name)


def main():
    """Main function for the app."""
    args = parse_arguments()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    ebird_api_key = os.getenv(ebird_api_key_name)
    if ebird_api_key == "0":
        sys.exit(
            "ebird API key must be specified in the "
            + ebird_api_key_name
            + " environment variable."
        )

    taxonomy = get_taxonomy.ebird_taxonomy()
    write_taxonomy_to_file(taxonomy, "reports/ebird_taxonomy.json")

    state = args.state
    state_list = get_state_list(args.review_species_file, taxonomy=taxonomy)
    counties = get_regions(
        token=ebird_api_key, rtype="subnational2", region=state
    )
    species = get_review_species(
        args.review_species_file, taxonomy, counties, state
    )

    records_to_review = []
    # for county in counties:
    for county in ["US-VA-003"]:
        # for date in dates:
        for day in [parser.parse("2025-01-12")]:
            records_to_review.extend(
                find_record_of_interest(
                    ebird_api_key, state_list, county, day, species
                )
            )
    if records_to_review:
        with open("reports/records_to_review.json", "wt", encoding="utf-8") as f:
            json.dump(records_to_review, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
