

import argparse
import json
import logging
from datetime import datetime

from ebird.api import get_regions, get_taxonomy

from get_reports import get_ebird_api_key, get_review_rules, get_state_list, get_records_to_review


def _parse_arguments() -> argparse.Namespace:
    """
    Parse and return command-line arguments for the get_reports script.

    Returns:
        argparse.Namespace: Parsed command-line arguments.

    Command-line arguments:
        --year (int, required): Year to review in YYYY format.
        --month (int, required): Month to review in MM format.
        --review_species_file (str, optional): Path to the JSON file containing species requiring review.
            Defaults to "get_reports/data/varcom_review_species.json".
        --state (str, optional): State to review in the format "US-XX".
            Defaults to "US-VA".
        --version: Displays the program version and exits.
        --verbose: Increases verbosity of the program output.
    """
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

def _save_records_to_file(records: list, year: int, month: int, state: str) -> None:
    """
    Save a list of records to a JSON file with metadata.
    This function creates a JSON file containing the provided records along with
    metadata such as the year, month, state, and the current date of the report.
    The file is saved in the "reports" directory with a filename indicating the
    year and month.
    Args:
        records (list): A list of records to be saved.
        year (int): The year associated with the records.
        month (int): The month associated with the records.
        state (str): The state associated with the records.
    Returns:
        None
    """
    if records:
        def get_current_date_string():
            return datetime.now().strftime("%Y-%m-%d")

        output_json = {
            "date of observations": f"{year:04d},{month:02d}",
            "state": state,
            "date of report": get_current_date_string(),
            "records": records,
        }
        with open(
            f"reports/records_to_review_{year:04d}_{month:02d}.json",
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
    state = args.state
    state_list = get_state_list.get_state_list(args.review_species_file, taxonomy=taxonomy)
    counties = get_regions(
        token=ebird_api_key, rtype="subnational2", region=state
    )
    species = get_review_rules.get_review_rules(
        args.review_species_file, taxonomy, counties, state
    )
    records_to_review = get_records_to_review.get_records_to_review(
        ebird_api_key, state_list, counties, args.year, args.month, species
    )
    _save_records_to_file(records_to_review, args.year, args.month, state)


if __name__ == "__main__":
    main()
