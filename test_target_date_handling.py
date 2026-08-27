import unittest
from unittest.mock import patch

import api
import main


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


if __name__ == "__main__":
    unittest.main()
