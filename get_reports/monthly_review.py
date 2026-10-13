"""Run the monthly report workflow outside GitHub Actions."""

import argparse
import logging
import os
import smtplib
import ssl
import subprocess
import sys
from datetime import date
from email.message import EmailMessage
from pathlib import Path
import tomllib

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _month_two_months_ago(today: date | None = None) -> tuple[int, int]:
    """Return the year and month two months before today."""
    today = today or date.today()
    month_index = today.year * 12 + today.month - 1 - 2
    year, month_index = divmod(month_index, 12)
    return year, month_index + 1


def _parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate and email the monthly VARCOM review report."
    )
    parser.add_argument(
        "--year", type=int, help="Report year (defaults to two months ago)"
    )
    parser.add_argument(
        "--month", type=int, choices=range(1, 13), help="Report month (1-12)"
    )
    parser.add_argument("--verbose", action="store_true")
    email_mode = parser.add_mutually_exclusive_group()
    email_mode.add_argument(
        "--no-email",
        action="store_true",
        help="Generate the report without emailing it",
    )
    email_mode.add_argument(
        "--email-only",
        action="store_true",
        help="Email an existing document without rerunning the API query",
    )
    args = parser.parse_args(argv)
    if (args.year is None) != (args.month is None):
        parser.error("--year and --month must be supplied together")
    return args


def _run_module(module: str, *arguments: str) -> None:
    subprocess.run(
        [sys.executable, "-m", module, *arguments],
        cwd=PROJECT_ROOT,
        check=True,
    )


def _configured_recipients() -> list[str]:
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as config_file:
        config = tomllib.load(config_file)
    try:
        recipients = config["tool"]["get_reports"]["monthly_review"][
            "recipients"
        ]
    except KeyError as error:
        raise ValueError(
            "Configure tool.get_reports.monthly_review.recipients in pyproject.toml"
        ) from error
    if not isinstance(recipients, list) or not all(
        isinstance(address, str) and address.strip() for address in recipients
    ):
        raise ValueError("Configured monthly report recipients must be non-empty strings")
    return [address.strip() for address in recipients]


def _send_email(document_path: Path, year: int, month: int) -> None:
    username = os.getenv("MAIL_USERNAME")
    password = os.getenv("MAIL_PASSWORD")
    if not username or not password:
        raise ValueError("MAIL_USERNAME and MAIL_PASSWORD must be set to send email")
    if not document_path.is_file():
        raise FileNotFoundError(f"Review document not found: {document_path}")

    mail_to = os.getenv("MAIL_TO")
    recipients = (
        [address.strip() for address in mail_to.split(",") if address.strip()]
        if mail_to is not None
        else _configured_recipients()
    )
    if not recipients:
        raise ValueError("MAIL_TO must contain at least one recipient")

    message = EmailMessage()
    message["Subject"] = "VARCOM Monthly Review Document"
    message["From"] = os.getenv("MAIL_FROM", "varcom.records@gmail.com")
    message["To"] = ", ".join(recipients)
    message.set_content(
        f"Monthly VARCOM report for {year:04d}-{month:02d} is ready."
    )
    message.add_attachment(
        document_path.read_bytes(),
        maintype="application",
        subtype="vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=document_path.name,
    )

    with smtplib.SMTP_SSL(
        "smtp.gmail.com", 465, context=ssl.create_default_context()
    ) as smtp:
        smtp.login(username, password)
        smtp.send_message(message)
    logging.info("Sent review document to %s", ", ".join(recipients))


def main(argv: list[str] | None = None) -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    args = _parse_arguments(argv)
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    year, month = (
        (args.year, args.month)
        if args.year is not None
        else _month_two_months_ago()
    )
    report_path = (
        PROJECT_ROOT
        / "reports"
        / f"records_to_review_{year:04d}_{month:02d}.json"
    )
    document_path = (
        PROJECT_ROOT / "reports" / f"review_{year:04d}_{month:02d}.docx"
    )

    if not args.email_only:
        (PROJECT_ROOT / "reports").mkdir(exist_ok=True)
        previous_mtime = (
            report_path.stat().st_mtime_ns if report_path.exists() else None
        )
        report_arguments = ["--year", str(year), "--month", str(month)]
        if args.verbose:
            report_arguments.insert(0, "--verbose")
        _run_module("get_reports.get_reports", *report_arguments)

        if not report_path.is_file() or (
            previous_mtime is not None
            and report_path.stat().st_mtime_ns == previous_mtime
        ):
            logging.info("No new records were written for %04d-%02d", year, month)
            return 0

        document_arguments = [
            "--input",
            str(report_path.relative_to(PROJECT_ROOT)),
            "--output",
            str(document_path.relative_to(PROJECT_ROOT)),
        ]
        if args.verbose:
            document_arguments.append("--verbose")
        _run_module("get_reports.create_review_document", *document_arguments)

    if not args.no_email:
        _send_email(document_path, year, month)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())