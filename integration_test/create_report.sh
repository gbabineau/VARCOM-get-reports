mkdir -p reports
# Create a file named records_to_review_2021_04_09.json in the reports directory.
poetry run python -m get_reports.get_reports --year 2021 --month 04 --day 09 --region US-VA-003

# Check the contents of the file to see if it contains the string S85143932.
grep S85143932 reports/records_to_review_2021_04_09.json
poetry run python -m  get_reports.create_review_document  --input reports/records_to_review_2021_04_09.json --output reports/review_2021_04_09.docx

# Since the .docx file is not a text file, convert it to a text file first
# and then search for the string S85143932 in the text file.

poetry run python -m integration_test.doc2text  --input reports/review_2021_04_09.docx --output reports/review_2021_04_09.txt
grep S85143932 reports/records_to_review_2021_04_09.txt
