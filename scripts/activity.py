"""Developer activity tracker.

Log what you worked on, list entries, and summarise time by project.

Log line format: ``<ISO timestamp> | <project> | <message>``
Older two-field lines (``<timestamp> | <message>``) are still read and
are assigned to the project "general".
"""

import argparse
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

DEFAULT_LOG = Path(__file__).resolve().parent.parent / "activity.log"
DEFAULT_PROJECT = "general"


def record_activity(message, project=DEFAULT_PROJECT, log=DEFAULT_LOG, now=None):
    """Append one entry to the log and return the written line."""
    message = " ".join(str(message).split())
    project = " ".join(str(project).split()).replace("|", "/") or DEFAULT_PROJECT
    if not message:
        raise ValueError("message must not be empty")
    message = message.replace("|", "/")
    stamp = (now or datetime.now().astimezone()).isoformat(timespec="seconds")
    line = f"{stamp} | {project} | {message}"
    with Path(log).open("a", encoding="utf-8") as file:
        file.write(line + "\n")
    return line


def read_entries(log=DEFAULT_LOG):
    """Return a list of (timestamp, project, message). Malformed lines are skipped."""
    path = Path(log)
    if not path.exists():
        return []
    entries = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        parts = [p.strip() for p in raw.split(" | ", 2)]
        if len(parts) == 2:
            parts = [parts[0], DEFAULT_PROJECT, parts[1]]
        if len(parts) != 3:
            continue
        try:
            stamp = datetime.fromisoformat(parts[0])
        except ValueError:
            continue
        entries.append((stamp, parts[1], parts[2]))
    return entries


def summarize(entries):
    """Return {project: entry_count}, most active first."""
    counts = Counter(project for _, project, _ in entries)
    return dict(counts.most_common())


def build_parser():
    parser = argparse.ArgumentParser(description="Track your development activity.")
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG, help="log file path")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="record an activity")
    add.add_argument("message")
    add.add_argument("-p", "--project", default=DEFAULT_PROJECT)

    lst = sub.add_parser("list", help="show recent entries")
    lst.add_argument("-n", "--limit", type=int, default=10)
    lst.add_argument("-p", "--project")

    sub.add_parser("summary", help="entry counts per project")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == "add":
        try:
            record_activity(args.message, args.project, args.log)
        except ValueError as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1
        print("Activity recorded.")
        return 0

    entries = read_entries(args.log)
    if args.command == "list":
        if args.project:
            entries = [e for e in entries if e[1] == args.project]
        for stamp, project, message in entries[-max(args.limit, 0):]:
            print(f"{stamp:%Y-%m-%d %H:%M}  [{project}]  {message}")
        return 0

    summary = summarize(entries)
    if not summary:
        print("No activity recorded yet.")
    for project, count in summary.items():
        print(f"{project}: {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
