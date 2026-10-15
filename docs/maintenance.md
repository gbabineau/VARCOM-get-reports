# Maintenance

## Taxonomy Updates

Regardless of this utility, the taxonomy used by birders changes every year. VARCOM uses the [American Ornithological Society Checklist of North and Middle American Birds](http://checklist.americanornithology.org/). This utility uses the [eBird taxonomy](https://science.ebird.org/en/use-ebird-data/the-ebird-taxonomy) for accessing eBird data. At least for the birds on the officil state list, the names used in both are the same (2025). When updates to those are made, the state list has to change as well.

1. State List (a list of birds seen in the state). For example, this is [Virginia's Official State Checklist](https://www.virginiabirds.org/offical-state-checklist).
1. Review list. Certain birds, while already on the state list do also require review in Virginia and other states may do the same. This means that even if a bird is on the official list, the review committee still reviews the record to help ensure integrity of records in the state. This is [Virginia's review list](https://www.virginiabirds.org/varcom-review-list)

## Virginia List Updates

Once the changes are made to the official lists, this utility has data files that also need updating. See [this documentation](docs\review_species_json_description.md) for details.

## Tokens

## eBird API key

Accessing eBird by the API (Application Programming Interface) requires an API key.

1. Request and obtain an [API key](https://ebird.org/api/keygen).

1. Add the key to the project-root `.env` file as `EBIRDAPIKEY=your_key`.

## gmail app password

The monthly report runner sends the review document through Gmail SMTP. Create
an App password for the sending account and add these values to the project-root
`.env` file:

1. [Create an App password](https://support.google.com/accounts/answer/185833?hl=en) for `Mail`.
1. Set `MAIL_USERNAME` to the Gmail address and `MAIL_PASSWORD` to its App password.
1. Default recipients are listed under `[tool.get_reports.monthly_review]` in `pyproject.toml`. Optionally set `MAIL_TO` as a comma-separated override and `MAIL_FROM` as the sender address.

Keep `.env` private and do not commit it.

## Monthly report runner

Run from the project directory to generate and email the report for two months
ago:

```shell
poetry run python -m get_reports.monthly_review
```

The runner has no six-hour job timeout. If an API run is interrupted or fails,
rerun it with the same `--year` and `--month`; county progress is checkpointed
and unfinished work resumes. If document generation succeeded but email failed,
retry delivery without repeating the API query:

```shell
poetry run python -m get_reports.monthly_review --year YYYY --month MM --email-only
```

Use `--no-email` to generate the report and document without sending mail. To
run it automatically on Linux, the systemd user timer below is recommended over
cron: it catches up after downtime, keeps logs in the journal, and can run as
your normal user. The schedule is 1:13 AM on the second day of each month in the
host's local timezone.

### Configure the systemd timer

The examples assume the repository is at
`~/Documents/gitprojects/VARCOM-get-reports` and Poetry is `/usr/bin/poetry`.
Adjust `WorkingDirectory` or `ExecStart` if yours differ. Check Poetry's path
with `command -v poetry`.

Create the user-unit directory:

```shell
mkdir -p ~/.config/systemd/user
```

Create `~/.config/systemd/user/varcom-monthly-report.service`:

```ini
[Unit]
Description=Generate and email the monthly VARCOM review report

[Service]
Type=oneshot
WorkingDirectory=%h/Documents/gitprojects/VARCOM-get-reports
ExecStart=/usr/bin/poetry run python -u -m get_reports.monthly_review --verbose
TimeoutStartSec=infinity
```

`TimeoutStartSec=infinity` is important: it prevents systemd from terminating
the API run after its default start timeout. The runner reads credentials from
the project-root `.env` file. Keep that file private (for example, run
`chmod 600 .env`).

Create `~/.config/systemd/user/varcom-monthly-report.timer`:

```ini
[Unit]
Description=Run the VARCOM monthly report on the fifteenth day of each month

[Timer]
OnCalendar=*-*-15 01:13:00
Persistent=true
Unit=varcom-monthly-report.service

[Install]
WantedBy=timers.target
```

Before enabling the schedule, test the service manually and inspect its output:

```shell
systemctl --user daemon-reload
systemctl --user start varcom-monthly-report.service
systemctl --user status varcom-monthly-report.service
journalctl --user -u varcom-monthly-report.service --no-pager
```

The service uses the recipient list in `pyproject.toml`, unless `MAIL_TO` is set
in `.env`; that variable overrides the list. Keep it set to your address for
testing, and remove or update it before the first scheduled run to send to the
full configured list.

Enable the timer after the manual test succeeds:

```shell
systemctl --user enable --now varcom-monthly-report.timer
systemctl --user list-timers varcom-monthly-report.timer
```

For the timer to run while you are logged out and after a reboot, enable lingering
for your account (this may require administrator privileges):

```shell
sudo loginctl enable-linger "$USER"
```

To inspect future runs, use `systemctl --user list-timers`.
To view the log of the latest use `systemctl --user status varcom-monthly-report.service`

SonarQube is not required for operation but is required in the continuous integration to ensure that quality standards are met.

1. Obtain an account and then [token](https://sonarcloud.io/account/security)
1. Store the value in `SONAR_TOKEN` in the [Actions secrets and variables](https://github.com/gbabineau/VARCOM-get-reports/settings/secrets/actions) configuration of the github repository.