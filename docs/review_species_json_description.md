# Review Species json structure

The review species json structure is stored in a file and use to define species that require review.  The overall structure looks like this:

```json
{
    "_comment" : "This file contains the species that are reviewed in the VARCOM report. There are two sections, review_species and exclude_groups.",
    "source" : "https://www.virginiabirds.org/varcom-review-list",
    "effective_date" : "2021-04-06",
    "review_species" : [
        { "comName" : "Black-bellied Whistling-Duck", "exclude" : ["Coastal Plain", "Piedmont"]},
        { "comName" : "Boat-tailed Grackle", "exclude" :["Isle of Wight", "York"], "unique_exclude_notes" : "except Eastern Coastal Plain, Isle of Wight Co. & York Co. east of Rt. 17."},
        { "comName" : "Lucy's Warbler"},

    ],
    "county_groups" : [
        { "name" : "group1", "counties": ["Arlington", "..."]},
        { "name" : "group2", "counties": ["Albemarle", "..."]},
        { "name" : "group3", "counties": ["Highland", "..."]}
    ]

}
```

## Overall information

  * _comment: a comment pertaining to the file as a whole
  * source" : Where the information to create this json is found. For example, in Virginia, this is our source of truth. "https://www.virginiabirds.org/varcom-review-list",
  * effective_date: When this information was captured from the source of truth. This is helpful, as for example taxonomy changes, and the species requiring review may change over time.

## Review species

These are species which are on the state list but still require review...sometimes in some circumstances only.

* review_species: A list of species that require review.
  * comName: The common name of the species. Must be identical to eBird taxonomy common name.
  * exclude: A list of counties or group names where this species is excluded from review requirements.
  * unique_exclude_notes: A comment which can be used when there are unique requirements where review is not required. In Virginia, for example, there are some birds that are regularly recorded from the Chesapeake Bay Bridge Tunnel which are unusual, even in the counties surrounting. These are printed.

## County groups

These groups can be used, for example to collect counties which are on the coast where records of mountain birds would be rare. For example, in Virginia, we organize counties in three groups, Coastal Plain, Piedmont, and Mountains and Valleys. A county should only be in one group. This does create challenges, when for example a county includes habitat that could reasonable qualify it for any of the groups.

* county_groups: A list of groups, each containing a name and a list of counties.
  * name: The name of the group.
  * counties: A list of county names that belong to this group.

