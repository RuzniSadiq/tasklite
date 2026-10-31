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
