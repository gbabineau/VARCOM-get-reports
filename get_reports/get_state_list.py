import json
import logging
import os


def get_state_list(file_name: str, taxonomy: list) -> dict:
    """
    Reads a JSON file containing a list of states and validates species against a given taxonomy.

    Args:
        file_name (str): The path to the JSON file containing the state list.
        taxonomy (list): A list of dictionaries representing the eBird taxonomy,
                         where each dictionary contains species information.

    Returns:
        dict: A dictionary containing the state list if the file exists and is valid,
              otherwise an empty dictionary.

    Logs:
        - Logs an error if the specified file does not exist.
        - Logs a warning for each species in the state list that is not found in the taxonomy.
        - Logs informational messages during the validation process.
    """
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
