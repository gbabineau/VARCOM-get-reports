""" Module to provide eBird API access with retries """
from datetime import date
import logging
from time import sleep

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
