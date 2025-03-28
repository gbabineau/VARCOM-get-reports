mkdir -p reports
poetry run get_reports.get_reports --year 2021 --month 04
poetry run get_reports.create_review_document  --input "reports/records_to_review_2021_04.json --output reports/review_2021_04.docx
grep S85143932 reports/review_2021_04.docx
