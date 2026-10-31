import json
import os
from datetime import date
from pathlib import Path

import pytest

import tasklite


@pytest.fixture(autouse=True)
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setenv("TASKLITE_DB", str(tmp_path / "tasks.json"))


def test_list_empty(capsys):
    assert tasklite.main(["list"]) == 0
    assert "No tasks." in capsys.readouterr().out


def test_add_list_done(capsys):
    tasklite.main(["add", "buy", "milk"])
    tasklite.main(["add", "write code"])
    tasklite.main(["done", "1"])
    capsys.readouterr()

    tasklite.main(["list"])
    out = capsys.readouterr().out.splitlines()
    assert out == ["[x] 1. buy milk", "[ ] 2. write code"]


def test_done_unknown_id(capsys):
    assert tasklite.main(["done", "42"]) == 1
    assert "No task with id 42" in capsys.readouterr().err


# --- issue #3: due dates ---------------------------------------------------


def _db() -> list:
    return json.loads(Path(os.environ["TASKLITE_DB"]).read_text())


def test_ac1_add_with_due_stores_date(capsys):
    assert tasklite.main(["add", "x", "--due", "2026-11-05"]) == 0
    assert "Added #1: x (due 2026-11-05)" in capsys.readouterr().out
    assert _db() == [{"id": 1, "title": "x", "done": False, "due": "2026-11-05"}]


def test_ac1_add_without_due_stores_no_field():
    tasklite.main(["add", "y"])
    assert _db() == [{"id": 1, "title": "y", "done": False}]


def test_ac2_list_shows_due_and_overdue(capsys):
    tasklite.main(["add", "future", "--due", "2999-01-01"])
    tasklite.main(["add", "past", "--due", "2000-01-01"])
    tasklite.main(["add", "past done", "--due", "2000-01-01"])
    tasklite.main(["done", "3"])
    tasklite.main(["add", "no due"])
    capsys.readouterr()

    tasklite.main(["list"])
    assert capsys.readouterr().out.splitlines() == [
        "[ ] 1. future (due 2999-01-01)",
        "[ ] 2. past (due 2000-01-01) [OVERDUE]",
        "[x] 3. past done (due 2000-01-01)",
        "[ ] 4. no due",
    ]


def test_ac2_overdue_boundary_is_strictly_before_today():
    today = date(2026, 11, 5)
    t: tasklite.Task = {"id": 1, "title": "x", "done": False, "due": "2026-11-05"}
    assert tasklite.format_task(t, today) == "[ ] 1. x (due 2026-11-05)"
    t["due"] = "2026-11-04"
    assert tasklite.format_task(t, today).endswith("[OVERDUE]")


@pytest.mark.parametrize("bad", ["2026-13-01", "2026-02-30", "tomorrow", "05/11/2026", ""])
def test_ac3_invalid_due_exits_2_with_clear_error(capsys, bad):
    with pytest.raises(SystemExit) as exc:
        tasklite.main(["add", "x", "--due", bad])
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "--due" in err and "invalid date" in err and "YYYY-MM-DD" in err
    assert not Path(os.environ["TASKLITE_DB"]).exists()


def test_ac4_legacy_tasks_without_due_load_and_list(capsys):
    Path(os.environ["TASKLITE_DB"]).write_text(
        json.dumps(
            [
                {"id": 1, "title": "old", "done": True},
                {"id": 2, "title": "older", "done": False},
            ]
        )
    )
    assert tasklite.main(["list"]) == 0
    assert capsys.readouterr().out.splitlines() == ["[x] 1. old", "[ ] 2. older"]
    tasklite.main(["add", "new", "--due", "2999-01-01"])
    assert [t.get("due") for t in _db()] == [None, None, "2999-01-01"]
