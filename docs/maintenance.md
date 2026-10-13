# Maintenance

## Taxonomy Updates

Regardless of this utility, the taxonomy used by birders changes every year. VARCOM uses the [American Ornithological Society Checklist of North and Middle American Birds](http://checklist.americanornithology.org/). This utility uses the [eBird taxonomy](https://science.ebird.org/en/use-ebird-data/the-ebird-taxonomy) for accessing eBird data. At least for the birds on the officil state list, the names used in both are the same (2025). When updates to those are made, the state list has to change as well.

1. State List (a list of birds seen in the state). For example, this is [Virginia's Official State Checklist](https://www.virginiabirds.org/offical-state-checklist).
1. Review list. Certain birds, while already on the state list do also require review in Virginia and other states may do the same. This means that even if a bird is on the official list, the review committee still reviews the record to help ensure integrity of records in the state. This is [Virginia's review list](https://www.virginiabirds.org/varcom-review-list)

## Virginia List Updates

Once the changes are made to the official lists, this utility has data files that also need updating. See [this documentation](docs\review_species_json_description.md) for details.

## Tokens

## eBird API key

Accessing eBird by the API (Application Programming Interface) requires an API key.

1. Request and obtain an [API key](https://ebird.org/api/keygen).

1. Add the key to the project-root `.env` file as `EBIRDAPIKEY=your_key`.

## gmail app password

The monthly report runner sends the review document through Gmail SMTP. Create
an App password for the sending account and add these values to the project-root
`.env` file:

1. [Create an App password](https://support.google.com/accounts/answer/185833?hl=en) for `Mail`.
1. Set `MAIL_USERNAME` to the Gmail address and `MAIL_PASSWORD` to its App password.
1. Default recipients are listed under `[tool.get_reports.monthly_review]` in `pyproject.toml`. Optionally set `MAIL_TO` as a comma-separated override and `MAIL_FROM` as the sender address.

Keep `.env` private and do not commit it.

## Monthly report runner

Run from the project directory to generate and email the report for two months
ago:

```shell
poetry run python -m get_reports.monthly_review
```

The runner has no six-hour job timeout. If an API run is interrupted or fails,
rerun it with the same `--year` and `--month`; county progress is checkpointed
and unfinished work resumes. If document generation succeeded but email failed,
retry delivery without repeating the API query:

```shell
poetry run python -m get_reports.monthly_review --year YYYY --month MM --email-only
```

Use `--no-email` to generate the report and document without sending mail. To
run it monthly, schedule the command with cron or a systemd timer on a machine
that stays online; for example, `13 1 2 * *` runs it at 1:13 on the second day
of each month in the host's local timezone.

## sonarqube token

SonarQube is not required for operation but is required in the continuous integration to ensure that quality standards are met.

1. Obtain an account and then [token](https://sonarcloud.io/account/security)
1. Store the value in `SONAR_TOKEN` in the [Actions secrets and variables](https://github.com/gbabineau/VARCOM-get-reports/settings/secrets/actions) configuration of the github repository.