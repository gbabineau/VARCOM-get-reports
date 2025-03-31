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

1. Store the value in `EBIRDAPIKEY` in the [Actions secrets and variables](https://github.com/gbabineau/VARCOM-get-reports/settings/secrets/actions) configuration of the github repository.

## gmail app password

The [workflow](.github\workflows\monthly_review.yaml) used to create the
monthly reports and email them relies on an action
[dawidd6/action-send-mail@v4](https://github.com/dawidd6/action-send-mail) that
authenticates to a mail server and then sends emails. It is set up to use the gmail smtp server which will work with gmail accounts.

1. [Create an App password](https://support.google.com/accounts/answer/185833?hl=en) for `Mail`.
1. Store the username (e.g. username@gmail.com) and app password as `MAIL_USERNAME` and `MAIL_PASSWORD` respectively in the [Actions secrets and variables](https://github.com/gbabineau/VARCOM-get-reports/settings/secrets/actions) configuration of the github repository.

## sonarqube token

SonarQube is not required for operation but is required in the continuous integration to ensure that quality standards are met.

1. Obtain an account and then [token](https://sonarcloud.io/account/security)
1. Store the value in `SONAR_TOKEN` in the [Actions secrets and variables](https://github.com/gbabineau/VARCOM-get-reports/settings/secrets/actions) configuration of the github repository.