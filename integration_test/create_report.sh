mkdir -p reports
poetry run python -m get_reports.get_reports --year 2021 --month 04
grep S85143932 reports/records_to_review_2021_04.json
poetry run python -m  get_reports.create_review_document  --input reports/records_to_review_2021_04.json --output reports/review_2021_04.docx
ls reports/review_2021_04.docx
