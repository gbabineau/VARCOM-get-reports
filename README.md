# VARCOM-get-reports

This utility was created for [VARCOM](https://www.virginiabirds.org/varcom) - interested in reports of select across the state of Virginia in  given time span

This code is shared so that any one else could use it. It is written so that another state could use it. However, it is unsupported. See [./LICENSE]. Feel free to submit pull requests on the [source]([https://github.com/gbabineau/VARCOM-get-reports]) to fix bugs or clone it and make your own version.

## Use
### get_reports

The `get_reports` script is used to generate reports of bird observations based on specific criteria. It queries the eBird API and processes the data to produce a report tailored to the needs of VARCOM or other organizations.

#### Usage

```bash
python get_reports.py --year YYYY -month MM -state STATE_CODE --input INPUT_FILE
```

#### Arguments

- `--year`: The year for the report in `YYYY` format.
- `--end_date`: The month number for the report in `MM` format.
- `--state`: The eBird state code (e.g., `US-VA` for Virginia) for which the report is generated.
- `--input`: The file path for the definition of state review rules

#### Example

```bash
python get_reports.py --year 2021 --month 04 --state US-VA -input varcom_review_species.json
```

---

### create_review_document.py

The `create_review_document.py` script is used to generate a review document based on the processed data. This document can be used to manually review and validate the observations.

#### Usage

```bash
python create_review_document.py --input INPUT_FILE --output output
```

#### Arguments

- `--input`: The file path to the input data (e.g., the output from `get_reports.py`).
- `--output`: The file path where the review document will be saved.

#### Example

```bash
python create_review_document.py --input reports/records_to_review_2021_04.json --output reports/january_review.docx
```

#### Notes

- Ensure that the input file is correctly formatted and contains the necessary data for review. See this [description](docs\review_species_json_description.md)
- The output file will be a Word document (`.docx`) that can be shared or printed for manual review.
- Customization of the review document format can be done by modifying the script.

## Issues

* Subspecies are not handled. We probably could but need to figure out a way to do it that doesn't require a lot of work like adding all the subspecies - think Downy Woodpecker (Eastern) for example that we really don't need to see. I figure it isn't priority and will let ideas percolate before implementing anything.

* Note that for any county, the first observation of a species for every day will be included. THis means, for example, if two individuals of the same species are seen in the same day, only one will be listed. This is a limitation of the API we are using. To limit records it will send the last or the first. I chose to have it send the last. To get all the records on that day, we would have to download the data.

* There will be an entry for every day that a species is seen in a county, even if it is thought to be the same individual. Of course there is no way to know if it is the same individual (eBird can't say whether it was watched 24/7). So these things will have to be manually reviewed.

* Some rules are not implemented, like reviews not being needed in specific locations or parts of counties - like County X East of Route N.

### Customization

For the most part, behavior is driven by a [json file](get_reports/data/varcom_review_species.json) which is documented [here](docs\review_species_json_description.md)
