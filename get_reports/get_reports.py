"""Get eBird reports of interest."""

import argparse
import json
import logging
from datetime import datetime

from ebird.api import get_regions, get_taxonomy

from get_reports import (
    get_ebird_api_key,
    get_review_rules,
    get_state_list,
    get_records_to_review,
)


def _parse_arguments() -> argparse.Namespace:
    """
    Parse and return command-line arguments for the get_reports script.

    Returns:
        argparse.Namespace: Parsed command-line arguments.

    Command-line arguments:
        --year (int, required): Year to review in YYYY format.
        --month (int, required): Month to review in MM format.
        --input (str, optional): Path to the JSON file containing species requiring review.
            Defaults to "get_reports/data/varcom_review_species.json".
        --region (str, optional): State or county to review in the format US-SS, or US-SS-CCC.
            Defaults to "US-VA".
        --version: Displays the program version and exits.
        --verbose: Increases verbosity of the program output.
    """
    arg_parser = argparse.ArgumentParser(
        prog="get_reports", description="Get eBird reports of interest."
    )
    arg_parser.add_argument(
        "--year", type=int, help="Year to review YYYY", required=True
    )
    arg_parser.add_argument(
        "--month", type=int, help="Month to review MM", required=True
    )
    arg_parser.add_argument(
        "--day",
        type=int,
        help="Day to review DD. Defaults to 00 for all days in month.",
        required=False,
        default=0,
    )
    arg_parser.add_argument(
        "--input",
        help="Species requiring review",
        default="get_reports/data/varcom_review_species.json",
    )
    arg_parser.add_argument(
        "--region",
        help="Region to review in the format US-SS, or US-SS-CCC",
        default="US-VA",
    )
    arg_parser.add_argument(
        "--version", action="version", version="%(prog)s 0.0.0"
    )
    arg_parser.add_argument(
        "--verbose", action="store_true", help="increase verbosity"
    )
    return arg_parser.parse_args()


def _save_records_to_file(
    records: list, year: int, month: int, day: int, region: str
) -> None:
    """
    Save a list of records to a JSON file with metadata.
    This function creates a JSON file containing the provided records along with
    metadata such as the year, month, state, and the current date of the report.
    The file is saved in the "reports" directory with a filename indicating the
    year and month.
    Args:
        records (list): A list of records to be saved.
        year (int): The year associated with the records.
        day (int): The day associated with the records. 0, indicates all days
            in the month.
        month (int): The month associated with the records.
        region (str): The region associated with the records.
    Returns:
        None
    """
    if records:

        def get_current_date_string():
            return datetime.now().strftime("%Y-%m-%d")

        observation_date = (
            datetime(year, month, day).strftime("%Y-%m-%d")
            if day != 0
            else datetime(year, month, 1).strftime("%Y-%m")
        )
        output_json = {
            "date of observations": observation_date,
            "region": region,
            "date of report": get_current_date_string(),
            "records": records,
        }
        save_file_name = (
            f"reports/records_to_review_{year:04d}_{month:02d}.json"
            if day == 0
            else f"reports/records_to_review_{year:04d}_{month:02d}_{day:02d}.json"
        )
        with open(
            save_file_name,
            "wt",
            encoding="utf-8",
        ) as f:
            json.dump(output_json, f, ensure_ascii=False, indent=4)


def main():
    """
    Main function to execute the report generation process.
    This function parses command-line arguments, retrieves necessary data from
    the eBird API, processes taxonomy and review rules, and generates a list
    of records to review based on the specified parameters. The results are
    then saved to a file.
    Steps:
    1. Parse command-line arguments.
    2. Configure logging if verbose mode is enabled.
    3. Retrieve the eBird API key.
    4. Fetch taxonomy data using the eBird API key.
    5. Retrieve the state list based on the review species file and taxonomy.
    6. Fetch county-level regions for the specified state.
    7. Determine species to review based on review rules, taxonomy, and counties.
    8. Retrieve records to review for the specified year, month, and species.
    9. Save the records to a file.
    Args:
        None (arguments are parsed internally).
    Returns:
        None
    """
    args = _parse_arguments()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    ebird_api_key = get_ebird_api_key.get_ebird_api_key()
    taxonomy = get_taxonomy(ebird_api_key)
    region = args.region
    state = region[:5]
    state_list = get_state_list.get_state_list(args.input, taxonomy=taxonomy)
    county_list = get_regions(
        token=ebird_api_key, rtype="subnational2", region=state
    )
    if state == region:
        counties = county_list
    else:
        matching_county = next(
            (county for county in county_list if county["code"] == region),
            None,
        )
        if not matching_county:
            logging.error(
                "Region %s not found in county list of %s. Exiting.",
                region,
                state,
            )
            return
        counties = [matching_county]
    species = get_review_rules.get_review_rules(
        args.input, taxonomy, counties, state
    )
    records_to_review = get_records_to_review.get_records_to_review(
        ebird_api_key=ebird_api_key,
        state_list=state_list,
        counties=counties,
        year=args.year,
        month=args.month,
        day=args.day,
        review_species=species,
    )
    _save_records_to_file(
        records_to_review, args.year, args.month, args.day, region
    )


if __name__ == "__main__":
    main()
