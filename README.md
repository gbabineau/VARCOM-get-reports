# VARCOM-get-reports

This utility was created for [VARCOM](https://www.virginiabirds.org/varcom) - interested in reports of select across the state of Virginia in  given time span

This code is shared so that any one else could use it. It is written so that another state could use it. However, it is unsupported. See [./LICENSE]. Feel free to submit pull requests on the [source]([https://github.com/gbabineau/VARCOM-get-reports]) to fix bugs or clone it and make your own version.

## Use


## Issues

* Note that for any county, the first observation of a species for every day will be included. THis means, for example, if two individuals of the same species are seen in the same day, only one will be listed. This is a limitation of the API we are using. To limit records it will send the last or the first. I chose to have it send the last. To get all the records on that day, we would have to download the data.

* There will be an entry for every day that a species is seen in a county, even if it is thought to be the same individual. Of course there is no way to know if it is the same individual (eBird can't say whether it was watched 24/7). So these things will have to be manually reviewed.

* Some rules are not implemented, like reviews not being needed in specific locations or parts of counties - like County X East of Route N.

### Customization

For the most part, behavior is driven by a [json file](get_reports/data/varcom_review_species.json) which is documented [here](docs\review_species_json_description.md)
