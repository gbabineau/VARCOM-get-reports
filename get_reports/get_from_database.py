""" get information by reading EBD """

def get_historic_observations_from_database(
    database: dict,
    area=str,
    day=str,
    category=str,
) -> list:
    """ Read observations from a filtered EBD """
    day_string = day.strftime("%Y-%m-%d")
    observations_of_interest = [
        obs
        for obs in database
        if obs.get("county") == area
        and obs.get("category") == category
        and obs["obsDt"][:10] == day_string
    ]
    return observations_of_interest
