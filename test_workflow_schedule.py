import re
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


WORKFLOW_PATH = Path(__file__).parent / ".github" / "workflows" / "main.yml"


def scheduled_local_time(workflow_text):
    schedule_match = re.search(
        r'^\s+schedule:\s*\n'
        r'\s+- cron:\s*["\'](\d+)\s+(\d+)\s+\*\s+\*\s+\*["\']\s*\n'
        r'\s+timezone:\s*["\']([^"\']+)["\']\s*$',
        workflow_text,
        re.MULTILINE,
    )
    if not schedule_match:
        raise AssertionError("A daily cron schedule and timezone are required")

    minute, hour = map(int, schedule_match.groups()[:2])
    timezone = ZoneInfo(schedule_match.group(3))
    return datetime(2026, 8, 31, hour, minute, tzinfo=timezone)


class WorkflowScheduleTests(unittest.TestCase):
    def test_daily_crawl_is_scheduled_for_0637_kst(self):
        workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")

        scheduled_at = scheduled_local_time(workflow_text)

        self.assertEqual(
            scheduled_at,
            datetime(2026, 8, 31, 6, 37, tzinfo=ZoneInfo("Asia/Seoul")),
        )


if __name__ == "__main__":
    unittest.main()
