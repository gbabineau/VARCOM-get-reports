mkdir -p reports
poetry run python -m  get_reports.get_reports --year 2021 --month 04
grep  S85143932 reports\records_to_review_2021_04.json