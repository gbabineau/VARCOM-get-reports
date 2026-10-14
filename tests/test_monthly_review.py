from datetime import date
import ssl
import subprocess
from unittest.mock import MagicMock, patch

import pytest

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


def test_parse_arguments_requires_year_and_month_together():
    with pytest.raises(SystemExit):
        monthly_review._parse_arguments(["--year", "2026"])


@patch("get_reports.monthly_review.smtplib.SMTP_SSL")
def test_send_email_uses_override_and_verified_tls(
    mock_smtp_ssl, tmp_path, monkeypatch
):
    document = tmp_path / "review.docx"
    document.write_bytes(b"docx contents")
    monkeypatch.setenv("MAIL_USERNAME", "sender@example.com")
    monkeypatch.setenv("MAIL_PASSWORD", "app-password")
    monkeypatch.setenv("MAIL_TO", "one@example.com, two@example.com")
    smtp = mock_smtp_ssl.return_value.__enter__.return_value

    monthly_review._send_email(document, 2026, 8)

    mock_smtp_ssl.assert_called_once()
    context = mock_smtp_ssl.call_args.kwargs["context"]
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True
    smtp.login.assert_called_once_with("sender@example.com", "app-password")
    message = smtp.send_message.call_args.args[0]
    assert message["To"] == "one@example.com, two@example.com"
    assert message["Subject"] == "VARCOM Monthly Review Document"
    assert list(message.iter_attachments())[0].get_filename() == "review.docx"


@patch("get_reports.monthly_review.smtplib.SMTP_SSL")
def test_send_email_uses_configured_recipients(
    mock_smtp_ssl, tmp_path, monkeypatch
):
    document = tmp_path / "review.docx"
    document.write_bytes(b"docx contents")
    (tmp_path / "pyproject.toml").write_text(
        '[tool.get_reports.monthly_review]\nrecipients = ["configured@example.org"]\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(monthly_review, "PROJECT_ROOT", tmp_path)
    monkeypatch.setenv("MAIL_USERNAME", "sender@example.com")
    monkeypatch.setenv("MAIL_PASSWORD", "app-password")
    monkeypatch.delenv("MAIL_TO", raising=False)

    monthly_review._send_email(document, 2026, 8)

    message = mock_smtp_ssl.return_value.__enter__.return_value.send_message.call_args.args[0]
    assert message["To"] == "configured@example.org"


def test_send_email_requires_credentials(tmp_path, monkeypatch):
    document = tmp_path / "review.docx"
    document.write_bytes(b"docx contents")
    monkeypatch.delenv("MAIL_USERNAME", raising=False)
    monkeypatch.delenv("MAIL_PASSWORD", raising=False)

    with pytest.raises(ValueError, match="MAIL_USERNAME and MAIL_PASSWORD"):
        monthly_review._send_email(document, 2026, 8)


def test_send_email_requires_existing_document(tmp_path, monkeypatch):
    monkeypatch.setenv("MAIL_USERNAME", "sender@example.com")
    monkeypatch.setenv("MAIL_PASSWORD", "app-password")

    with pytest.raises(FileNotFoundError, match="Review document not found"):
        monthly_review._send_email(tmp_path / "missing.docx", 2026, 8)


@patch("get_reports.monthly_review.smtplib.SMTP_SSL")
def test_send_email_rejects_empty_recipient_override(
    mock_smtp_ssl, tmp_path, monkeypatch
):
    document = tmp_path / "review.docx"
    document.write_bytes(b"docx contents")
    monkeypatch.setenv("MAIL_USERNAME", "sender@example.com")
    monkeypatch.setenv("MAIL_PASSWORD", "app-password")
    monkeypatch.setenv("MAIL_TO", " , ")

    with pytest.raises(ValueError, match="at least one recipient"):
        monthly_review._send_email(document, 2026, 8)
    mock_smtp_ssl.assert_not_called()


def test_main_generates_document_and_skips_email_when_requested(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(monthly_review, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(monthly_review, "load_dotenv", MagicMock())
    calls = []

    def create_report(module, *arguments):
        calls.append((module, arguments))
        if module == "get_reports.get_reports":
            report = tmp_path / "reports" / "records_to_review_2026_08.json"
            report.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(monthly_review, "_run_module", create_report)
    send_email = MagicMock()
    monkeypatch.setattr(monthly_review, "_send_email", send_email)

    result = monthly_review.main(
        ["--year", "2026", "--month", "8", "--verbose", "--no-email"]
    )

    assert result == 0
    assert [call[0] for call in calls] == [
        "get_reports.get_reports",
        "get_reports.create_review_document",
    ]
    assert "--verbose" in calls[0][1]
    assert "--verbose" in calls[1][1]
    send_email.assert_not_called()


def test_main_stops_when_report_was_not_written(tmp_path, monkeypatch):
    monkeypatch.setattr(monthly_review, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(monthly_review, "load_dotenv", MagicMock())
    run_module = MagicMock()
    monkeypatch.setattr(monthly_review, "_run_module", run_module)
    send_email = MagicMock()
    monkeypatch.setattr(monthly_review, "_send_email", send_email)

    result = monthly_review.main(["--year", "2026", "--month", "8"])

    assert result == 0
    run_module.assert_called_once_with(
        "get_reports.get_reports", "--year", "2026", "--month", "8"
    )
    send_email.assert_not_called()


def test_main_stops_when_report_is_unchanged(tmp_path, monkeypatch):
    monkeypatch.setattr(monthly_review, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(monthly_review, "load_dotenv", MagicMock())
    report = tmp_path / "reports" / "records_to_review_2026_08.json"
    report.parent.mkdir()
    report.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(monthly_review, "_run_module", MagicMock())
    send_email = MagicMock()
    monkeypatch.setattr(monthly_review, "_send_email", send_email)

    result = monthly_review.main(["--year", "2026", "--month", "8"])

    assert result == 0
    send_email.assert_not_called()


def test_main_email_only_skips_report_generation(tmp_path, monkeypatch):
    monkeypatch.setattr(monthly_review, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(monthly_review, "load_dotenv", MagicMock())
    run_module = MagicMock()
    monkeypatch.setattr(monthly_review, "_run_module", run_module)
    send_email = MagicMock()
    monkeypatch.setattr(monthly_review, "_send_email", send_email)

    result = monthly_review.main(
        ["--year", "2026", "--month", "8", "--email-only"]
    )

    assert result == 0
    run_module.assert_not_called()
    send_email.assert_called_once_with(
        tmp_path / "reports" / "review_2026_08.docx", 2026, 8
    )


def test_run_module_propagates_subprocess_failure():
    with patch(
        "get_reports.monthly_review.subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "python"),
    ) as run:
        with pytest.raises(subprocess.CalledProcessError):
            monthly_review._run_module("get_reports.get_reports", "--year", "2026")

    assert run.call_args.kwargs["check"] is True