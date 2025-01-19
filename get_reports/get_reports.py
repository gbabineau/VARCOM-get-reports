"""
Main function for the get_reports application which presents a quiz of bird photos
based on a definition of species, and time of year (to handle different)
plumages.
"""

import argparse
import logging
import os
import sys
from dateutil import parser

from ebird.api import get_historic_observations, get_regions

ebird_api_key_name = "EBIRDAPIKEY"


def main():
    """Main function for the app."""
    arg_parser = argparse.ArgumentParser(
        prog="photo-id", description="Get eBird reports of interest."
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
    # getting the review list for counties like this: https://www.virginiabirds.org/varcom-review-list/
    # this should really read the entire list from a file that also considered that not all counties require review
    # This proof of concept is just for two species
    species = ["wesmea", "paibun"]
    state="US-VA"
    counties = get_regions(token=ebird_api_key, rtype='subnational2', region=state)
    for county in counties:
        area = county['code']
        # the date should really be a range entered by the user. Fixed for this proof of concept.
        date = parser.parse("2025-01-12")
        observations = get_historic_observations(
            token=ebird_api_key, area=area, date=date, category="species"
        )
        county_listed = False
        for observation in observations:
            if observation["speciesCode"] in species:
                if not county_listed:
                    print(
                        f"Observations for county:{county['name']}"
                    )
                    county_listed = True
                print(observation)


if __name__ == "__main__":
    main()
