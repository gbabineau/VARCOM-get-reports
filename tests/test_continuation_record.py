# pylint: disable=W0212, C0116, C0114
import json
from pathlib import Path

import pytest

from get_reports.continuation_record import ContinuationRecord


def test_init_creates_file_when_missing(tmp_path):
    ContinuationRecord._continuation_file = str(
        tmp_path / "continuation_data.dat"
    )
    initial = ["CountyA", "CountyB"]
    cr = ContinuationRecord(initial)
    p = Path(ContinuationRecord._continuation_file)
    assert p.exists()
    content = json.loads(p.read_text(encoding="utf-8"))
    assert content == {"counties": [], "records": []}
    assert cr.counties() == initial
    assert cr.records() == []


def test_init_reads_existing_file_and_computes_remaining(tmp_path):
    ContinuationRecord._continuation_file = str(
        tmp_path / "continuation_data.dat"
    )
    p = Path(ContinuationRecord._continuation_file)
    data = {"counties": ["County1"], "records": ["rec1"]}
    p.write_text(json.dumps(data), encoding="utf-8")
    cr = ContinuationRecord(["County1", "County2", "County3"])
    assert cr.counties() == ["County2", "County3"]
    assert cr.records() == ["rec1"]


def test_update_writes_county_and_records_to_file(tmp_path):
    ContinuationRecord._continuation_file = str(
        tmp_path / "continuation_data.dat"
    )
    p = Path(ContinuationRecord._continuation_file)
    initial_data = {"counties": [], "records": []}
    p.write_text(json.dumps(initial_data), encoding="utf-8")
    cr = ContinuationRecord(["CountyX"])
    cr.update({"id": "CountyX"}, ["r1", "r2"])
    content = json.loads(p.read_text(encoding="utf-8"))
    assert content["counties"] == [{"id": "CountyX"}]
    assert content["records"] == ["r1", "r2"]
    # object's in-memory records are not updated by update(); ensure current behavior
    assert cr.records() == []


def test_complete_deletes_file(tmp_path):
    ContinuationRecord._continuation_file = str(
        tmp_path / "continuation_data.dat"
    )
    p = Path(ContinuationRecord._continuation_file)
    p.write_text(json.dumps({"counties": [], "records": []}), encoding="utf-8")
    cr = ContinuationRecord(["Any"])
    cr.complete()
    assert not p.exists()


def test_update_logs_error_when_file_missing(tmp_path, caplog):
    ContinuationRecord._continuation_file = str(
        tmp_path / "continuation_data.dat"
    )
    # create then remove the file to simulate missing file at update time
    cr = ContinuationRecord(["One"])
    p = Path(ContinuationRecord._continuation_file)
    if p.exists():
        p.unlink()
    caplog.clear()
    cr.update({"id": "One"}, ["r"])
    assert "Continuation file doesn't exist." in caplog.text


def test_init_logs_and_reraises_file_error(tmp_path, monkeypatch, caplog):
    ContinuationRecord._continuation_file = str(
        tmp_path / "continuation_data.dat"
    )

    def fail_open(self, *args, **kwargs):
        raise OSError("read failed")

    monkeypatch.setattr(Path, "open", fail_open)

    with pytest.raises(OSError, match="read failed"):
        ContinuationRecord(["One"])

    assert "Error loading continuation or creating record" in caplog.text


def test_update_logs_and_reraises_file_error(tmp_path, monkeypatch, caplog):
    ContinuationRecord._continuation_file = str(
        tmp_path / "continuation_data.dat"
    )
    path = Path(ContinuationRecord._continuation_file)
    path.write_text(json.dumps({"counties": [], "records": []}), encoding="utf-8")
    cr = ContinuationRecord(["One"])

    def fail_open(self, *args, **kwargs):
        raise OSError("update failed")

    monkeypatch.setattr(Path, "open", fail_open)

    with pytest.raises(OSError, match="update failed"):
        cr.update({"id": "One"}, ["r"])

    assert "Error updating continuation" in caplog.text


def test_complete_logs_when_file_is_missing(tmp_path, caplog):
    ContinuationRecord._continuation_file = str(
        tmp_path / "continuation_data.dat"
    )
    cr = ContinuationRecord(["One"])
    Path(ContinuationRecord._continuation_file).unlink()
    caplog.clear()

    cr.complete()

    assert "Continuation file doesn't exist." in caplog.text


def test_complete_logs_and_reraises_unlink_error(tmp_path, monkeypatch, caplog):
    ContinuationRecord._continuation_file = str(
        tmp_path / "continuation_data.dat"
    )
    cr = ContinuationRecord(["One"])

    def fail_unlink(self, *args, **kwargs):
        raise OSError("delete failed")

    monkeypatch.setattr(Path, "unlink", fail_unlink)

    with pytest.raises(OSError, match="delete failed"):
        cr.complete()

    assert "Error deleting continuation record" in caplog.text
