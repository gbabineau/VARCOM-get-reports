import os
import sys
from ebird.api import get_taxonomy

ebird_api_key_name = "EBIRDAPIKEY"


def ebird_taxonomy() -> list:
    """
    Retrieves the ebird taxonomy.

    Returns:
        list: The ebird taxonomy.
    """
    taxonomy = []
    ebird_api_key = os.getenv(ebird_api_key_name)
    if ebird_api_key == "0":
        sys.exit(
            "ebird API key must be specified in the "
            + ebird_api_key_name
            + " environment variable."
        )
    taxonomy = get_taxonomy(ebird_api_key)

    return taxonomy
