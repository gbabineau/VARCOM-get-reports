# Get filename from command line arguments
args <- commandArgs(trailingOnly = TRUE)
if (length(args) == 0) {
    stop("Please provide a filename for the EBD as a command line argument")
}
filename <- args[1]
# Read eBird database (tab-separated file)
cat("Reading file:", filename, "\n")
ebird_data <- read.delim(filename,
                quote = "",
                row.names = NULL,
                stringsAsFactors = FALSE)
#ebird_data <- read.delim("gum.txt")
# Define common names of interest
# Read species list from JSON file
cat("Getting species of interest:\n")
varcom_species <- jsonlite::fromJSON("get_reports/data/varcom_review_species.json")
review_species <- varcom_species$review_species
review_species <- review_species$comName
cat("Filtering Data:\n")

# Filter observations for birds in the list
filtered_data <- ebird_data[ebird_data$COMMON.NAME %in% review_species &
                             ebird_data$HAS.MEDIA == 1 &
                             ebird_data$APPROVED == 1, ]

output_file <- "EBD/ebird_filtered.csv"
cat("Writing",output_file," with ", nrow(filtered_data), " records\n")

# Write to CSV
write.csv(filtered_data, output_file, row.names = FALSE)