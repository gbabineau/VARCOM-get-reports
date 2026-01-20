# VARCOM-get-reports

This utility was created for [VARCOM](https://www.virginiabirds.org/varcom) - interested in reports of select across the state of Virginia in  given time span

This code is shared so that any one else could use it. It is written so that another state could use it. However, it is unsupported. See [./LICENSE]. Feel free to submit pull requests on the [source]([https://github.com/gbabineau/VARCOM-get-reports]) to fix bugs or clone it and make your own version.

## Use

This can be used in two ways.

1. One way is using the eBird API. This has some issues because the API does not provide ALL the data. However it is much faster to use, for example for monthly reports to get a sense of what is going on. This can be fully automated.

1. The second way is to use the EBD (eBird Database). This is slower but gets
the all the data. Before being able to use this method you will have to download
and use a program to filter the data. Downloading the data requires some manual
work (requesting the data and waiting for a download link to be emailed) and
and then running an R script to filter the data. See [downloading and filtering](#downloading-and-filtering-the-ebird-dataset) instructions.

### get_reports

The `get_reports` script is used to generate reports of bird observations based on specific criteria. It queries the eBird API and processes the data to produce a report tailored to the needs of VARCOM or other organizations.

#### Usage

```bash
python get_reports.py --year YYYY -month MM [--day DD] -state STATE_CODE --input INPUT_FILE
```

#### Arguments

- `--year`: The year for the report in `YYYY` format.
- `--month`: The month number for the report in `MM` format.
- '--day': The day of the report - defaults to 0 which will create a report for the entire month
- `--region`: The eBird region (e.g., `US-VA` for Virginia, or `US-VA-003` for Albemarle County, virginia) for which the report is to be generated.
- `--input`: The file path for the definition of state list and review rules
- `--EBD <FILE>`: Optional file with filtered ebird data if EBD is to be used.

#### Example

```bash
python get_reports.py --year 2021 --month 04 --day 09 --region US-VA-003 -input varcom_review_species.json
```

---

### create_review_document.py

The `create_review_document.py` script is used to generate a review document based on the processed data. This document can be used to manually review and validate the observations.

#### Use of create_review_document

```bash
python create_review_document.py --input INPUT_FILE --output OUTPUT_FILE
```

#### Arguments fo create_review_document

- `--input`: The file path to the input data (e.g., the output from `get_reports.py`).
- `--output`: The file path where the review document will be saved.

#### Example using create_review_document

```bash
python create_review_document.py --input reports/records_to_review_2021_04.json --output reports/january_review.docx
```

#### Notes

- Ensure that the input file is correctly formatted and contains the necessary data for review. See this [description](docs\review_species_json_description.md)
- The output file will be a Word document (`.docx`) that can be shared or printed for manual review.
- Customization of the review document format can be done by modifying the script.

## Issues

1. Subspecies are not handled. We probably could but need to figure out a way to do it that doesn't require a lot of work like adding all the subspecies - think Downy Woodpecker (Eastern) for example that we really don't need to see. I figure it isn't priority and will let ideas percolate before implementing anything.

1. There will be an entry for every day that a species is seen in a county, even if it is thought to be the same individual. Of course there is no way to know if it is the same individual (eBird can't say whether it was watched 24/7). So these things will have to be manually reviewed.

1. Some rules are not implemented, like reviews not being needed in specific locations or parts of counties - like County X East of Route N.

    There are a few geographic quirks that will be hard to capture in eBird, and may simply require manual intervention:

1. Pelagic - There are some species that are not reviewable in the pelagic zone, but would be reviewable anywhere from shore. The pelagic zone in eBird will still show up as either Accomack, Northampton, or Virginia Beach. These records should be few and far between, but we will just have to be conscious of that when identifying which ones are actually reviewable. As a start, the scripts eliminate records using the eBird pelagic protocol Unfortunately, not everyone uses the protocol. Going further, we could probably tell also by lat/lon using a gis library and a defined polygon.

1. Ridge lines - In many of the counties along the ridge, the crest of the ridge is the county line. However, in the strictest definition of a physiographic province, the Piedmont ends at the foothills and the slope is part of the Mountains & Valleys. Thus, for example, a Ruffed Grouse at Peaks of Otter in Bedford would be captured by your script, but wouldn't merit review since it is actually in the M&V part of Bedford county. Again, there is no easy way to handle this with the script, so I think we will just have to remember to manually remove M&V species. I would think it will be relatively few cases. Possibly we could get smart with using a gis library (or online?) and getting elevation of the location.

1. Weird quirks in the Review List - There are a few instances of weirdly specific things in the Review List that the scripts won't easily capture. For example, Long-billed Curlew is not reviewable in the "barrier island lagoon system," which is not well-defined. In theory that means it would be reviewable elsewhere in Accomack or Northampton. Similarly, some species use roads as dividers (reviewable north of I-64, for example), which obviously don't correspond with counties. Frankly, I am not sure where that process originated and why it is so random and inconsistent. Most, if not all, of those are legacy things. I would probably have to look at the individual species in question, but maybe we want to consider just abandoning these and making the Review List conform to county and/or physiographic province boundaries.

### Issues specific to using the API

1. For any county, the first observation of a species for every day will be included. THis means, for example, if two individuals of the same species are seen in the same day, only one will be listed. This is a limitation of the API we are using. To limit records it will send the last or the first. I chose to have it send the last. To get all the records on that day, we would have to download the data. See [Downloading the eBird Dataset].

    Though, we could possibly do the following, if that checklist does not have the media, get all checklists for that day using checklist feed API then use the view checklist api to get each checklist, search them if they have that species and have the media. these records could be appended to the first and added to the review.

    To be eligible for expedited review, a record must include media (audio, video, or photo). Currently the script does not check for media. However, (see above) only one observation per day is included per species. If there is a second observation that has media, it would not be found. So this will have to be manually reviewed. To assist the reviewer, the report lists whether the record has media because if they do have media, it is reviewable. If it doesn't have media, though, it is possible that another observation one of the days had media. In practice, even the information about the single observation per day does help.

## Downloading and filtering the eBird Dataset

### Downloading

If, rather than using the API, the entire dataset for the state is used, which allows more accurate reporting as for example using the API only provides the first (or last) observation on a given day and if that observation does not have media, the siting would not be reviewable even though there may be a later observation on the same day with media.

To download the data you have to obtain permission. See information about the [eBird Basic Dataset (EBD)](https://science.ebird.org/en/use-ebird-data/download-ebird-data-products).  Then request the ability to download. After approval you will get an [access link](https://ebird.org/data/download).

Download the data for all species, in Virginia (or your state) only, with your date range of interest. Sampling event data and unvetted data are not needed. Minimizing the data set to only the area and dates of your interest will make a smaller dataset and help improve the speed of the report generation.

You will then get an email when your download is ready. Once you receive the email, download it and extract.

### Filtering

Filtering requires the R language to be installed. Once R is installed:

```shell
Rscript R_preprocess_database/preprocess.R [your downloaded file]
```

This will create the file EBD/ebird_filtered.csv which should be passed to
get_reports with the --EBD argument.

## Customization and Maintenance

For the most part, behavior is driven by a [json file](get_reports/data/varcom_review_species.json). See documentation for [the format of this file](docs\review_species_json_description.md).

[Maintenance](docs\maintenance.md) (probably yearly) is required to handle updates to taxonomies and state lists.
