"""tasklite: a tiny to-do CLI."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import TypedDict, cast


class Task(TypedDict):
    id: int
    title: str
    done: bool


DEFAULT_DB = Path.home() / ".tasklite.json"


def db_path() -> Path:
    return Path(os.environ.get("TASKLITE_DB", DEFAULT_DB))


def load() -> list[Task]:
    path = db_path()
    if not path.exists():
        return []
    return cast(list[Task], json.loads(path.read_text() or "[]"))


def save(tasks: list[Task]) -> None:
    db_path().write_text(json.dumps(tasks, indent=2))


def add(title: str) -> Task:
    tasks = load()
    task: Task = {
        "id": max((t["id"] for t in tasks), default=0) + 1,
        "title": title,
        "done": False,
    }
    tasks.append(task)
    save(tasks)
    return task


def done(task_id: int) -> Task:
    tasks = load()
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = True
            save(tasks)
            return t
    raise KeyError(task_id)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tasklite", description="A tiny to-do CLI.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_add = sub.add_parser("add", help="add a task")
    p_add.add_argument("title", nargs="+")
    sub.add_parser("list", help="list tasks")
    p_done = sub.add_parser("done", help="mark a task done")
    p_done.add_argument("id", type=int)
    args = parser.parse_args(argv)

    if args.cmd == "add":
        t = add(" ".join(args.title))
        print(f"Added #{t['id']}: {t['title']}")
    elif args.cmd == "list":
        tasks = load()
        if not tasks:
            print("No tasks.")
        for t in tasks:
            print(f"[{'x' if t['done'] else ' '}] {t['id']}. {t['title']}")
    elif args.cmd == "done":
        try:
            t = done(args.id)
        except KeyError:
            print(f"No task with id {args.id}", file=sys.stderr)
            return 1
        print(f"Completed #{t['id']}: {t['title']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())