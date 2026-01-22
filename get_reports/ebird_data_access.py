""" Module to provide eBird API and EBD access """
from datetime import date
import logging
from time import sleep
import pandas as pd

from ebird.api import get_checklist, get_historic_observations


def get_checklist_with_retry(api_key: str, observation: str) -> list:
    """
    Calls the eBird API get_checklist with retries
    """
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
    area: str,
    day: date,
    category: str,
    rank: str,
    detail: str,
) -> list:
    """
    Calls the eBird API get_historic_observations with retries
    """
    attempts = 0
    while attempts < 3:
        try:
            return get_historic_observations(
                token=token,
                area=area,
                date=day,
                category=category,
                rank=rank,
                detail=detail,
            )
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
                    exc,
                )
                raise

def read_database(database_file: str) -> list:
    """ Reads an EBD file and formats it for use similar to what the API
        provides.
    """
    logging.info("Reading observations from %s", database_file)

    try:
        df = pd.read_csv(
            database_file,
            dtype={"24": str},
            usecols=[3, 5, 10, 19, 20, 30, 31, 34, 37, 46, 47],
        )
        df.columns = [
            "category",
            "comName",
            "howMany",
            "subnational2Name",
            "county",
            "obsDt",
            "obsTime",
            "subId",
            "protocolId",
            "media",
            "approved",
        ]

        database = df.to_dict("records")
    except FileNotFoundError:
        logging.error("database file not found: %s", database_file)
        return []
    except OSError as e:
        logging.error("Error reading database: %s. Error %s", database_file, e)
        return []

    # append time to date so that it works the same was as the api
    for observation in database:
        observation["obsDt"] = (
            f"{observation['obsDt']} {observation['obsTime']}"
        )
    return database

def get_historic_observations_from_database(
    database: dict,
    area=str,
    day=str,
    category=str,
) -> list:
    """ Read observations from a database formatted as above """
    day_string = day.strftime("%Y-%m-%d")
    observations_of_interest = [
        obs
        for obs in database
        if obs.get("county") == area
        and obs.get("category") == category
        and obs["obsDt"][:10] == day_string
    ]
    return observations_of_interest