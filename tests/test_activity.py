import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import activity  # noqa: E402


class ActivityTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.log = Path(self.dir.name) / "activity.log"

    def tearDown(self):
        self.dir.cleanup()

    def test_record_and_read(self):
        now = datetime(2026, 1, 5, 9, 30, tzinfo=timezone.utc)
        activity.record_activity("wrote tests", "tracker", self.log, now=now)
        entries = activity.read_entries(self.log)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0][1:], ("tracker", "wrote tests"))

    def test_empty_message_rejected(self):
        with self.assertRaises(ValueError):
            activity.record_activity("   ", log=self.log)
        self.assertFalse(self.log.exists())

    def test_pipe_characters_do_not_break_format(self):
        activity.record_activity("a | b", "x|y", self.log)
        (_, project, message), = activity.read_entries(self.log)
        self.assertEqual((project, message), ("x/y", "a / b"))

    def test_legacy_two_field_lines_are_kept(self):
        self.log.write_text("2026-01-01T10:00:00+05:30 | old entry\n", encoding="utf-8")
        activity.record_activity("new entry", "p", self.log)
        entries = activity.read_entries(self.log)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0][1], "general")

    def test_malformed_lines_skipped_not_deleted(self):
        self.log.write_text("garbage\n", encoding="utf-8")
        activity.record_activity("ok", log=self.log)
        self.assertEqual(len(activity.read_entries(self.log)), 1)
        self.assertIn("garbage", self.log.read_text(encoding="utf-8"))

    def test_missing_log_is_empty(self):
        self.assertEqual(activity.read_entries(self.log), [])

    def test_summary_orders_by_count(self):
        for project in ["a", "b", "b"]:
            activity.record_activity("x", project, self.log)
        summary = activity.summarize(activity.read_entries(self.log))
        self.assertEqual(list(summary.items()), [("b", 2), ("a", 1)])

    def test_cli(self):
        self.assertEqual(activity.main(["--log", str(self.log), "add", "hi", "-p", "demo"]), 0)
        self.assertEqual(activity.main(["--log", str(self.log), "summary"]), 0)
        self.assertEqual(activity.main(["--log", str(self.log), "add", " "]), 1)


if __name__ == "__main__":
    unittest.main()
