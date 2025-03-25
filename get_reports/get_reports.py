""" """

import argparse
import json
import logging
import os
import sys
from dateutil import parser
from datetime import date
from calendar import monthrange

from ebird.api import get_historic_observations, get_regions
from get_reports import get_taxonomy
from datetime import datetime

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

    if not os.path.exists(file_name):
        logging.error("File %s does not exist.", file_name)
        return {}
    with open(file_name, "rt", encoding="utf-8") as f:
        state_list = json.load(f)["state_list"]
    logging.info("Checking species in state list against eBird taxonomy.")
    for species in state_list:
        if not any(
            taxon["comName"] == species["comName"] for taxon in taxonomy
        ):
            logging.warning(
                "Species %s not found in eBird taxonomy", species["comName"]
            )

    return state_list


def parse_arguments() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        prog="get_reports", description="Get eBird reports of interest."
    )
    arg_parser.add_argument("--year", type=int, help="Year to review YYYY", required=True)
    arg_parser.add_argument(
        "--month", type=int, help="Month to review MM", required=True
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


def county_in_list_or_group(county_name : str, exclusion_list: list, county_groups: list) -> bool:
    included = False
    if county_name in exclusion_list:
        included = True
    else:
        for exclusion in exclusion_list:
            groups = county_groups
            group = next(
                (g for g in groups if g["name"] == exclusion), None
            )
            if group and county_name in group["counties"]:
                included = True
    return included

def is_new_record(observation: dict, state_list : list)->bool:
    return observation.get("exoticCategory","") != 'X' and not any(
            species["comName"] == observation["comName"]
            for species in state_list
        )

def reviewable_species(observation: dict, species_to_review: list)->bool:
    return next(
                (
                    species
                    for species in species_to_review
                    if species["comName"] == observation["comName"]
                ),
                None,
            )

def find_record_of_interest(
    ebird_api_key: str,
    state_list: list,
    county: dict,
    day: date,
    review_species: dict,
) -> list:
    observations = get_historic_observations(
        token=ebird_api_key, area=county["code"], date=day, category="species", rank="create"
    )
    records_of_interest = []
    for observation in observations:
        if is_new_record(observation, state_list):
            logging.info(
                "Species %s not in state list. A new record?",
                observation["comName"],
            )
            records_of_interest.append(
                {"observation": observation, "new": True}
            )
        else:
            if matching_species := reviewable_species(observation, review_species["review_species"]):

                reviewable = True
                only_match = matching_species.get("only", [])
                if only_match:
                    reviewable = county_in_list_or_group(
                        county["name"],
                        only_match,
                        review_species.get("county_groups", []))
                elif county_in_list_or_group(
                    county["name"],
                    matching_species.get("exclude", []),
                    review_species.get("county_groups", []),
                ):
                    reviewable = False

                if reviewable:
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
                        }
                    )
    return records_of_interest


def write_taxonomy_to_file(taxonomy: list, file_name: str) -> None:

    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(taxonomy, f, ensure_ascii=False, indent=4)
    logging.info("Taxonomy written to %s", file_name)


def iterate_days_in_month(year: int, month: int):
    num_days = monthrange(year, month)[1]
    for day in range(1, num_days + 1):
        yield date(year, month, day)


def main():
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
    for county in counties:
        county_records = []
        for day in iterate_days_in_month(args.year, args.month):
            records_for_county = find_record_of_interest(
                ebird_api_key, state_list, county, day, species
            )
            if records_for_county:
                county_records.extend(records_for_county)
        if county_records:
            records_to_review.append(
                {"county": county["name"], "records": county_records}
            )
    if records_to_review:
        def get_current_date_string():
            return datetime.now().strftime("%Y-%m-%d")

        output_json = {
            "date of observations": f"{args.year:04d},{args.month:02d}",
            "state": state,
            "date of report": get_current_date_string(),
            "records": records_to_review
        }
        with open(
            f"reports/records_to_review_{args.year:04d}_{args.month:02d}.json",
            "wt",
            encoding="utf-8",
        ) as f:
            json.dump(output_json, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
