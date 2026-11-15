# Developer Activity

A small collection of programming experiments, utilities,
learning exercises, and development notes.

## Purpose

This repository tracks genuine development work and project progress.

## Activity tracker

`scripts/activity.py` is a dependency-free Python 3 CLI that logs what you
worked on and summarises it by project.

```bash
python scripts/activity.py add "Wrote unit tests" -p developer-activity
python scripts/activity.py list              # last 10 entries
python scripts/activity.py list -p demo -n 5 # filter by project
python scripts/activity.py summary           # entry counts per project
```

Entries are appended to `activity.log` (git-ignored, so your personal log
is never committed) as `timestamp | project | message`. Old two-field lines
are still read and shown under the project `general`.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Structure

- scripts/ - Python utilities
- tests/ - unit tests
- experiments/ - Programming experiments
- notes/ - Development notes
