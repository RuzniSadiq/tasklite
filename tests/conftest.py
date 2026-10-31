def pytest_terminal_summary(terminalreporter):  # type: ignore[no-untyped-def]
    """Print a line The Gibson can read to count tests (catches deleted tests)."""
    s = terminalreporter.stats
    kinds = ("passed", "failed", "error", "skipped", "xfailed", "xpassed")
    total = sum(len(s.get(k, [])) for k in kinds)
    skipped = len(s.get("skipped", []))
    terminalreporter.write_line(
        f"GIBSON_TEST_METRICS total={total} skipped={skipped} todo=0"
    )