"""


"""

import argparse
import json
import logging
import os
import sys
from dateutil import parser

from ebird.api import get_historic_observations, get_regions
from get_reports import get_taxonomy

ebird_api_key_name = "EBIRDAPIKEY"


def get_review_species(file_name :str, taxonomy : list, county_list : list) -> dict:
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
    for group in review_species["exclude_groups"]:
        for county in group["counties"]:
            if not any(d['name'] == county for d in county_list):
                logging.warning(
                    "County %s not found in ebirds list of counties for this state.", county
                )
    for species in review_species["review_species"]:
        if species["comName"] not in taxonomy:
            logging.warning(
                "Species %s not found in taxonomy", species["comName"]
            )
        for exclusion in species.get("exclude", []):
            if not any(d['name'] == exclusion for d in county_list) and not any(group['name'] == exclusion for group in review_species.get("exclude_groups",[])):
                logging.warning(
                    "Exclusion %s was not found as a group or county", exclusion
                )

    return review_species

def main():
    """Main function for the app."""
    arg_parser = argparse.ArgumentParser(
        prog="get_reports", description="Get eBird reports of interest."
    )
    arg_parser.add_argument(
        "--review_species_file",
        help="Species requiring review",
        default="get_reports/data/varcom_review_species.json",
    )
    arg_parser.add_argument(
        "--state", help="State to review", default="US-VA"
    )
    arg_parser.add_argument(
        "--version", action="version", version="%(prog)s 0.0.0"
    )
    arg_parser.add_argument(
        "--verbose", action="store_true", help="increase verbosity"
    )
    args = arg_parser.parse_args()

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


    state=args.state
    counties = get_regions(token=ebird_api_key, rtype='subnational2', region=state)
    species = get_review_species(args.review_species_file, taxonomy, counties)

    # for county in counties:
    #     area = county['code']
    #     # the date should really be a range entered by the user. Fixed for this proof of concept.
    #     date = parser.parse("2025-01-12")
    #     observations = get_historic_observations(
    #         token=ebird_api_key, area=area, date=date, category="species"
    #     )
    #     county_listed = False
    #     for observation in observations:
    #         if observation["speciesCode"] in species the right part of it:
    #             if not county_listed:
    #                 print(
    #                     f"Observations for county:{county['name']}"
    #                 )
    #                 county_listed = True
    #             print(observation)


if __name__ == "__main__":
    main()
