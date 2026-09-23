

def test_running_the_pass_twice_in_a_day_does_not_duplicate_an_event(tmp_path, monkeypatch):
    """Measured on 2026-09-23: one phone change appeared three times after three runs.

    The day's snapshot is overwritten by each run, so the diff baseline stays yesterday's and every
    run of that day re-detects the same change. An inflated trigger feed is worse than a quiet one:
    the whole point of a trigger is that it means something happened.
    """
    import base

    monkeypatch.setattr(base, "EVENTS_DIR", tmp_path)
    ev = {"date": "2026-09-23", "register": "amf-france", "company_slug": "seventure-partners",
          "company_name": "SEVENTURE PARTNERS", "field": "phone", "before": "0157950510",
          "after": "0158192270", "label": "telephone published or changed",
          "is_trigger": False, "woke": False}

    base.append_events([dict(ev)])
    base.append_events([dict(ev)])
    base.append_events([dict(ev, woke=True)])   # same change, different consequence for us

    lines = [l for l in (tmp_path / "2026-09.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == 1, f"the same change was logged {len(lines)} times"


def test_a_genuinely_different_change_is_still_appended(tmp_path, monkeypatch):
    """Dedup must not swallow real news — a second, different change on the same firm counts."""
    import base

    monkeypatch.setattr(base, "EVENTS_DIR", tmp_path)
    base_ev = {"date": "2026-09-23", "register": "amf-france", "company_slug": "x",
               "company_name": "X", "field": "phone", "before": "1", "after": "2",
               "label": "t", "is_trigger": False, "woke": False}
    base.append_events([dict(base_ev)])
    base.append_events([dict(base_ev, field="licence_type", before="A", after="B")])
    base.append_events([dict(base_ev, date="2026-09-24")])

    lines = [l for l in (tmp_path / "2026-09.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    # All three are distinct events and all three are September, so all three land in this file:
    # a different field is a different change, and the same change seen on a different day is a
    # separate observation worth keeping.
    assert len(lines) == 3
