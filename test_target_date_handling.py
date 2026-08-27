import os
import unittest
from contextlib import ExitStack
from datetime import datetime as real_datetime
from unittest.mock import patch

import api
import main
import spreadsheet


GETTER_NAMES = [
    "get_data_successbid_service",
    "get_data_successbid_service_nodesign",
    "get_data_successbid_construction",
    "get_data_newopen_service",
    "get_data_newopen_service_nodesign",
    "get_data_newopen_construction",
    "get_data_newopen_private",
    "get_data_successbid_private",
    "get_data_successbid_kwater",
    "get_data_successbid_lh",
    "get_data_scheduledbid_service",
]


class FixedKstDateTime(real_datetime):
    @classmethod
    def now(cls, tz=None):
        current = real_datetime(2026, 8, 27, 7, 37, 0)
        if tz is not None:
            return tz.localize(current)
        return current


class TargetDateHandlingTests(unittest.TestCase):
    def test_set_target_date_uses_explicit_date_for_query_bounds(self):
        api.set_target_date("2026-08-26", days_range_override=1)

        self.assertEqual(api.yesterday_date.isoformat(), "2026-08-26")
        self.assertEqual(api.start_date.date().isoformat(), "2026-08-26")
        self.assertEqual(api.inqry_bgn_dt, "202608260000")
        self.assertEqual(api.inqry_end_dt, "202608262359")

    def test_reset_messages_uses_target_date_string(self):
        with patch.object(main.api, "get_target_date_string", return_value="2026-08-26", create=True):
            main.reset_messages()

        self.assertEqual(main.message_bid, "*2026-08-26*\n")
        self.assertEqual(main.message_project, "*2026-08-26*\n")

    def test_set_target_date_defaults_to_previous_kst_day(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(api, "datetime", FixedKstDateTime):
                api.set_target_date()

        self.assertEqual(api.yesterday_date.isoformat(), "2026-08-26")
        self.assertEqual(api.inqry_bgn_dt, "202608260000")
        self.assertEqual(api.inqry_end_dt, "202608262359")

    def test_spreadsheet_target_date_defaults_to_previous_kst_day(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(spreadsheet, "datetime", FixedKstDateTime):
                self.assertEqual(spreadsheet.get_target_date_string(), "2026-08-26")

    def test_main_refreshes_target_date_from_environment_before_messages(self):
        api.set_target_date("2026-08-24")

        with ExitStack() as stack:
            stack.enter_context(patch.dict(os.environ, {"SCRAPE_TARGET_DATE": "2026-08-26"}, clear=True))
            stack.enter_context(patch.object(main.slack, "send_message"))
            stack.enter_context(patch.object(main.time, "sleep", return_value=None))
            stack.enter_context(patch.object(main, "print", create=True))
            stack.enter_context(patch.object(main.api_url, "SPREADSHEET_LINK", "https://example.com/sheet"))

            for getter_name in GETTER_NAMES:
                stack.enter_context(patch.object(main.api, getter_name, return_value=[]))

            main.main()

        self.assertEqual(api.yesterday_date.isoformat(), "2026-08-26")
        self.assertEqual(main.message_bid.splitlines()[0], "*2026-08-26*")


if __name__ == "__main__":
    unittest.main()
