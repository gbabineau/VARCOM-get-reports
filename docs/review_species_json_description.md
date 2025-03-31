# Review Species JSON Structure

The input file to `get_reports` is a json structured file file defines species that require review and organizes them into groups for clarity. And example of a file using this format is [this file](get_reports\data\varcom_review_species.json)

## Overall Information

* **_comment**: A comment providing context about the file.
* **source**: The source of truth for the information, e.g., [Virginia's review list](https://www.virginiabirds.org/varcom-review-list).
* **effective_date**: The date when the information was captured from the source of truth. This is useful for tracking changes over time, such as taxonomy updates or species review requirements.

## Official State list

This is the official state list of birds found in the state. If a bird is on this list, it does not require review unless it is on the [review_species list](#review-species). If the bird is not on this list it should be reviewed as a potential state record.

* **review_species**: A list of species requiring review.
  * **comName**: The common name of the species, aligned with eBird taxonomy.

## Review Species

These are species on the state list that require review, sometimes only under specific circumstances.

* **review_species**: A list of species requiring review.
  * **comName**: The common name of the species, aligned with eBird taxonomy.
  * **exclude**: A list of counties or group names where this species is excluded from review requirements.
  * **only**: A list of counties or group names which are the only places in the state where this observation requires review.
  * **unique_exclude_notes**: A comment for unique cases where review is not required. For example, in Virginia, some birds are regularly recorded from the Chesapeake Bay Bridge Tunnel but are unusual in surrounding counties.

## County Groups

These groups organize counties based on geographic or ecological characteristics. For example, in Virginia, counties are grouped into Coastal Plain, Piedmont, and Mountains and Valleys.

* **county_groups**: A list of groups, each containing a name, a list of counties, and a description.
  * **name**: The name of the group.
  * **counties**: A list of county names that belong to this group.
  * **description**: A brief explanation of the group's purpose or characteristics.

## Example JSON Structure

```json
{
  "_comment": "This file contains the species that are reviewed in the VARCOM report. There are two sections, review_species and exclude_groups.",
  "source": "https://www.virginiabirds.org/varcom-review-list",
  "effective_date": "2023-10-01",
  "review_species": [
    {
      "comName": "Black-bellied Whistling-Duck",
      "exclude": ["Coastal Plain", "Piedmont"],
    },
    {
      "comName": "Boat-tailed Grackle",
      "exclude": ["Isle of Wight", "York"],
      "unique_exclude_notes": "except Eastern Coastal Plain, Isle of Wight Co. & York Co. east of Rt. 17.",
    },
    {
      "comName": "Lucy's Warbler",
    }
  ],
  "county_groups": [
    {
      "name": "group1",
      "counties": ["Arlington", "..."],
      "description": "Northern Virginia counties."
    },
    {
      "name": "group2",
      "counties": ["Albemarle", "..."],
      "description": "Central Virginia counties."
    },
    {
      "name": "group3",
      "counties": ["Highland", "..."],
      "description": "Western mountain counties."
    }
  ]
}
```

## Additional Notes

* The `description` field in `county_groups` improves clarity about the purpose of each group.
