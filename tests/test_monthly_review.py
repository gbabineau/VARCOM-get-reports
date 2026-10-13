from datetime import date

from get_reports import monthly_review
from get_reports.monthly_review import _month_two_months_ago


def test_month_two_months_ago_rolls_over_year():
    assert _month_two_months_ago(date(2026, 2, 13)) == (2025, 12)


def test_month_two_months_ago_uses_same_year():
    assert _month_two_months_ago(date(2026, 10, 13)) == (2026, 8)


def test_configured_recipients_are_loaded_from_pyproject(tmp_path, monkeypatch):
    (tmp_path / "pyproject.toml").write_text(
        '[tool.get_reports.monthly_review]\nrecipients = ["review@example.org"]\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(monthly_review, "PROJECT_ROOT", tmp_path)

    assert monthly_review._configured_recipients() == ["review@example.org"]