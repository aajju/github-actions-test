import unittest
from contextlib import ExitStack
from unittest.mock import patch

import requests

import api
import api_url
import main


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


class JsonResponse:
    status_code = 200
    text = "json response"

    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload


class XmlResponse:
    status_code = 200
    text = "xml response"
    encoding = "utf-8"
    content = b"<response></response>"


class ScrapeErrorSlackMessageTests(unittest.TestCase):
    def setUp(self):
        api.reset_scrape_errors()
        main.message_bid = "*2026-09-06*\n"

    def test_final_slack_message_explains_collection_failures(self):
        errors = [
            {
                "source": "낙찰정보_용역(설계)",
                "message": (
                    "API 응답시간 초과 — 60초 제한으로 총 3회 요청했지만 실패했습니다. "
                    "이 항목은 0건이 아니라 수집 실패입니다."
                ),
            }
        ]

        with patch.object(main.api, "get_scrape_errors", return_value=errors, create=True), patch.object(
            main.api_url, "SPREADSHEET_LINK", "https://example.com/sheet"
        ), patch.object(main.slack, "send_message") as mock_send:
            main.process_data_bid([], "발주예정_용역")

        sent_message = mock_send.call_args.args[0]
        self.assertIn("⚠️ *수집 오류*", sent_message)
        self.assertIn("낙찰정보_용역(설계)", sent_message)
        self.assertIn("총 3회 요청", sent_message)
        self.assertIn("0건이 아니라 수집 실패", sent_message)

    def test_partial_page_error_does_not_claim_the_whole_category_failed(self):
        errors = [
            {
                "source": "나라장터 신규공고 용역 API",
                "message": "후속 페이지 오류로 일부 자료가 누락됐을 수 있습니다.",
            }
        ]

        summary = main.format_scrape_errors(errors)

        self.assertIn("일부 자료가 누락", summary)
        self.assertNotIn("0건이 아니라 수집 실패", summary)

    def test_main_clears_errors_from_a_previous_run(self):
        api._scrape_errors.append(
            {"source": "이전 실행", "message": "이미 끝난 오류입니다."}
        )

        with ExitStack() as stack:
            mock_send = stack.enter_context(patch.object(main.slack, "send_message"))
            stack.enter_context(patch.object(main.time, "sleep", return_value=None))
            stack.enter_context(
                patch.object(main.api_url, "SPREADSHEET_LINK", "https://example.com/sheet")
            )
            for getter_name in GETTER_NAMES:
                stack.enter_context(patch.object(main.api, getter_name, return_value=[]))

            main.main()

        sent_message = mock_send.call_args.args[0]
        self.assertNotIn("이전 실행", sent_message)
        self.assertNotIn("⚠️ *수집 오류*", sent_message)

    def test_successbid_scrape_omits_unused_announcement_detail_category(self):
        empty_response = JsonResponse(
            {"response": {"body": {"totalCount": 0}}}
        )
        original_numbers = api.bidNtceNos
        api.bidNtceNos = []
        main.message_bid = "*2026-09-07*\n"
        try:
            with patch("api.requests.get", return_value=empty_response):
                api.get_data_bid(api_url.URL_SUCCESSBID_SERVICE)
        finally:
            api.bidNtceNos = original_numbers

        self.assertNotIn("낙찰용역_w공고", main.message_bid)


class ApiErrorCollectionTests(unittest.TestCase):
    def setUp(self):
        api.reset_scrape_errors()

    def test_repeated_timeout_records_human_readable_error(self):
        with patch(
            "api.requests.get",
            side_effect=[requests.exceptions.Timeout(), requests.exceptions.Timeout()],
        ), patch("api.time.sleep"):
            response = api.request_get_with_retry(
                api_url.URL_SUCCESSBID_SERVICE,
                timeout=60,
                attempts=2,
                retry_delay=0,
            )

        self.assertIsNone(response)
        self.assertEqual(
            api.get_scrape_errors(),
            [
                {
                    "source": "나라장터 낙찰 용역 API",
                    "message": (
                        "API 응답시간 초과 — 60초 제한으로 총 2회 요청했지만 실패했습니다. "
                        "이 항목은 0건이 아니라 수집 실패입니다."
                    ),
                }
            ],
        )

    def test_http_error_records_status_without_exposing_request_url(self):
        response_400 = type("Response", (), {"status_code": 400})()

        with patch("api.requests.get", return_value=response_400), patch("api.time.sleep"):
            response = api.request_get_with_retry(
                api_url.URL_NEWOPEN_CONSTRUCTION,
                attempts=1,
                retry_delay=0,
            )

        self.assertIsNone(response)
        self.assertEqual(
            api.get_scrape_errors(),
            [
                {
                    "source": "나라장터 신규공고 공사 API",
                    "message": (
                        "API가 HTTP 400 오류를 반환했습니다. "
                        "이 항목은 0건이 아니라 수집 실패입니다."
                    ),
                }
            ],
        )
        self.assertNotIn(api_url.URL_NEWOPEN_CONSTRUCTION, str(api.get_scrape_errors()))

    def test_network_error_does_not_expose_exception_details(self):
        exception = requests.exceptions.RequestException(
            "connection failed for https://example.com?serviceKey=TOP-SECRET"
        )

        with patch("api.requests.get", side_effect=exception), patch("api.time.sleep"):
            response = api.request_get_with_retry(
                api_url.URL_SUCCESSBID_SERVICE,
                attempts=1,
                retry_delay=0,
            )

        self.assertIsNone(response)
        self.assertEqual(
            api.get_scrape_errors(),
            [
                {
                    "source": "나라장터 낙찰 용역 API",
                    "message": (
                        "API 연결 중 네트워크 오류가 발생했습니다. "
                        "이 항목은 0건이 아니라 수집 실패입니다."
                    ),
                }
            ],
        )
        self.assertNotIn("TOP-SECRET", str(api.get_scrape_errors()))

    def test_api_errors_identify_the_failing_source(self):
        sources = [
            (api_url.URL_SCHEDULED_BID_SERVICE, "나라장터 발주예정 용역 API"),
            (api_url.URL_SUCCESSBID_SERVICE, "나라장터 낙찰 용역 API"),
            (api_url.URL_SUCCESSBID_CONSTRUCTION, "나라장터 낙찰 공사 API"),
            (api_url.URL_NEWOPEN_SERVICE, "나라장터 신규공고 용역 API"),
            (api_url.URL_NEWOPEN_CONSTRUCTION, "나라장터 신규공고 공사 API"),
            (api_url.URL_NEWOPEN_PRIVATE_SERVICE, "나라장터 민간 신규공고 용역 API"),
            (api_url.URL_NEWOPEN_PRIVATE_CONSTRUCTION, "나라장터 민간 신규공고 공사 API"),
            (api_url.URL_SUCCESSBID_PRIVATE, "나라장터 민간 낙찰 API"),
            (api_url.URL_SUCCESSBID_KWATER_SERVICE, "K-water 낙찰 용역 API"),
            (api_url.URL_SUCCESSBID_KWATER_CONSTRUCTION, "K-water 낙찰 공사 API"),
            (api_url.URL_SUCCESSBID_LH_SERVICE, "LH 계약정보 API"),
            (api_url.URL_NEWOPEN_SERVICE_WITH_NUMBER, "나라장터 공고 상세정보 API"),
        ]
        response_503 = type("Response", (), {"status_code": 503})()

        for url, expected_source in sources:
            with self.subTest(source=expected_source):
                api.reset_scrape_errors()
                with patch("api.requests.get", return_value=response_503):
                    api.request_get_with_retry(url, attempts=1, retry_delay=0)

                self.assertEqual(api.get_scrape_errors()[0]["source"], expected_source)

    def test_malformed_json_response_records_parsing_error(self):
        malformed_response = JsonResponse({"response": {}})

        with patch("api.request_get_with_retry", return_value=malformed_response):
            items = api.get_data_bid(api_url.URL_NEWOPEN_SERVICE)

        self.assertEqual(items, [])
        self.assertEqual(
            api.get_scrape_errors(),
            [
                {
                    "source": "나라장터 신규공고 용역 API",
                    "message": (
                        "API 응답 데이터 형식이 올바르지 않아 처리하지 못했습니다. "
                        "이 항목은 0건이 아니라 수집 실패입니다."
                    ),
                }
            ],
        )

    def test_zero_results_are_not_reported_as_parsing_error(self):
        empty_response = JsonResponse(
            {"response": {"body": {"totalCount": 0}}}
        )

        with patch("api.request_get_with_retry", return_value=empty_response):
            items = api.get_data_bid(api_url.URL_NEWOPEN_SERVICE)

        self.assertEqual(items, [])
        self.assertEqual(api.get_scrape_errors(), [])

    def test_positive_total_without_items_is_reported_as_parsing_error(self):
        malformed_response = JsonResponse(
            {"response": {"body": {"totalCount": 1}}}
        )

        with patch("api.request_get_with_retry", return_value=malformed_response):
            items = api.get_data_bid(api_url.URL_NEWOPEN_SERVICE)

        self.assertEqual(items, [])
        self.assertIn("수집 실패", api.get_scrape_errors()[0]["message"])

    def test_request_parameters_do_not_log_api_key(self):
        empty_response = JsonResponse(
            {"response": {"body": {"totalCount": 0}}}
        )

        with patch.object(api.api_url, "API_KEY", "TOP-SECRET"), patch(
            "api.request_get_with_retry", return_value=empty_response
        ), patch("api.print") as mock_print:
            api.get_data_bid(api_url.URL_NEWOPEN_SERVICE)

        printed_output = " ".join(str(call.args) for call in mock_print.call_args_list)
        self.assertNotIn("TOP-SECRET", printed_output)

    def test_malformed_json_in_secondary_query_records_parsing_error(self):
        malformed_response = JsonResponse({"response": {}})

        with patch("api.request_get_with_retry", return_value=malformed_response):
            items = api.get_data_bid(api_url.URL_NEWOPEN_SERVICE, sign=False)

        self.assertEqual(items, [])
        self.assertEqual(
            api.get_scrape_errors(),
            [
                {
                    "source": "나라장터 신규공고 용역 API",
                    "message": (
                        "API 응답 데이터 형식이 올바르지 않아 처리하지 못했습니다. "
                        "이 항목은 0건이 아니라 수집 실패입니다."
                    ),
                }
            ],
        )

    def test_zero_results_in_secondary_query_are_not_an_error(self):
        empty_response = JsonResponse(
            {"response": {"body": {"totalCount": 0}}}
        )

        with patch("api.request_get_with_retry", return_value=empty_response):
            items = api.get_data_bid(api_url.URL_NEWOPEN_SERVICE, sign=False)

        self.assertEqual(items, [])
        self.assertEqual(api.get_scrape_errors(), [])

    def test_malformed_lh_xml_records_parsing_error(self):
        with patch("api.request_get_with_retry", return_value=XmlResponse()):
            items = api.get_data_bid(api_url.URL_SUCCESSBID_LH_SERVICE)

        self.assertEqual(items, [])
        self.assertEqual(
            api.get_scrape_errors(),
            [
                {
                    "source": "LH 계약정보 API",
                    "message": (
                        "API 응답 데이터 형식이 올바르지 않아 처리하지 못했습니다. "
                        "이 항목은 0건이 아니라 수집 실패입니다."
                    ),
                }
            ],
        )

    def test_malformed_detail_response_records_parsing_error(self):
        malformed_response = JsonResponse({"response": {}})
        original_numbers = api.bidNtceNos
        api.bidNtceNos = ["TEST-001"]
        try:
            with patch("api.request_get_with_retry", return_value=malformed_response), patch(
                "api.time.sleep"
            ):
                items = api.get_data_w_number()
        finally:
            api.bidNtceNos = original_numbers

        self.assertEqual(items, [])
        messages = [error["message"] for error in api.get_scrape_errors()]
        self.assertIn(
            "API 상세정보 응답 데이터 형식이 올바르지 않아 일부 자료를 처리하지 못했습니다.",
            messages,
        )
        self.assertIn(
            "상세정보 1건을 모두 수집하지 못했습니다. 이 항목은 0건이 아니라 수집 실패입니다.",
            messages,
        )

    def test_zero_detail_results_are_not_reported_as_parsing_error(self):
        empty_response = JsonResponse(
            {"response": {"body": {"totalCount": 0}}}
        )
        original_numbers = api.bidNtceNos
        api.bidNtceNos = ["TEST-001"]
        try:
            with patch("api.request_get_with_retry", return_value=empty_response), patch(
                "api.time.sleep"
            ):
                items = api.get_data_w_number()
        finally:
            api.bidNtceNos = original_numbers

        self.assertEqual(items, [])
        self.assertEqual(api.get_scrape_errors(), [])

    def test_positive_detail_total_without_items_is_reported_as_parsing_error(self):
        malformed_response = JsonResponse(
            {"response": {"body": {"totalCount": 1}}}
        )
        original_numbers = api.bidNtceNos
        api.bidNtceNos = ["TEST-001"]
        try:
            with patch("api.request_get_with_retry", return_value=malformed_response), patch(
                "api.time.sleep"
            ):
                items = api.get_data_w_number()
        finally:
            api.bidNtceNos = original_numbers

        self.assertEqual(items, [])
        messages = [error["message"] for error in api.get_scrape_errors()]
        self.assertTrue(any("데이터 형식" in message for message in messages))
        self.assertTrue(any("0건이 아니라 수집 실패" in message for message in messages))

    def test_malformed_followup_page_is_reported_without_crashing(self):
        first_page = JsonResponse(
            {"response": {"body": {"totalCount": 1000, "items": []}}}
        )
        malformed_second_page = JsonResponse({"response": {}})

        with patch(
            "api.request_get_with_retry",
            side_effect=[first_page, malformed_second_page],
        ):
            try:
                items = api.get_data_bid(api_url.URL_NEWOPEN_SERVICE)
            except (KeyError, requests.exceptions.JSONDecodeError) as exc:
                self.fail(f"후속 페이지 파싱 오류가 전파되었습니다: {exc}")

        self.assertEqual(items, [])
        self.assertEqual(
            api.get_scrape_errors(),
            [
                {
                    "source": "나라장터 신규공고 용역 API",
                    "message": "API 후속 페이지의 데이터 형식이 올바르지 않아 일부 자료를 처리하지 못했습니다.",
                }
            ],
        )

    def test_failed_followup_request_preserves_first_page_data(self):
        first_page_items = [{"bidNtceNo": "FIRST-PAGE"}]
        first_page = JsonResponse(
            {"response": {"body": {"totalCount": 1000, "items": first_page_items}}}
        )

        with patch(
            "api.requests.get",
            side_effect=[first_page, requests.exceptions.Timeout(), requests.exceptions.Timeout(), requests.exceptions.Timeout()],
        ), patch("api.time.sleep"), patch(
            "api.filter_items_bid", return_value=first_page_items
        ):
            items = api.get_data_bid(api_url.URL_NEWOPEN_SERVICE)

        self.assertEqual(items, first_page_items)
        self.assertEqual(
            api.get_scrape_errors(),
            [
                {
                    "source": "나라장터 신규공고 용역 API",
                    "message": (
                        "API 응답시간 초과 — 60초 제한으로 총 3회 요청했지만 실패했습니다. "
                        "이 때문에 후속 페이지 일부가 누락됐을 수 있습니다."
                    ),
                }
            ],
        )

    def test_malformed_secondary_followup_page_is_reported_without_crashing(self):
        first_page = JsonResponse(
            {"response": {"body": {"totalCount": 1000, "items": []}}}
        )
        malformed_second_page = JsonResponse({"response": {}})

        with patch(
            "api.request_get_with_retry",
            side_effect=[first_page, malformed_second_page],
        ):
            try:
                items = api.get_data_bid(api_url.URL_NEWOPEN_SERVICE, sign=False)
            except (KeyError, requests.exceptions.JSONDecodeError) as exc:
                self.fail(f"보조 조회 후속 페이지 파싱 오류가 전파되었습니다: {exc}")

        self.assertEqual(items, [])
        self.assertEqual(
            api.get_scrape_errors()[0]["message"],
            "API 후속 페이지의 데이터 형식이 올바르지 않아 일부 자료를 처리하지 못했습니다.",
        )

    def test_failed_secondary_followup_request_preserves_first_page_data(self):
        first_page_items = [{"bidNtceNo": "FIRST-PAGE"}]
        first_page = JsonResponse(
            {"response": {"body": {"totalCount": 1000, "items": first_page_items}}}
        )

        with patch(
            "api.requests.get",
            side_effect=[first_page, requests.exceptions.Timeout(), requests.exceptions.Timeout(), requests.exceptions.Timeout()],
        ), patch("api.time.sleep"), patch(
            "api.filter_items_bid2", return_value=first_page_items
        ):
            items = api.get_data_bid(api_url.URL_NEWOPEN_SERVICE, sign=False)

        self.assertEqual(items, first_page_items)
        self.assertEqual(
            api.get_scrape_errors()[0]["message"],
            (
                "API 응답시간 초과 — 60초 제한으로 총 3회 요청했지만 실패했습니다. "
                "이 때문에 후속 페이지 일부가 누락됐을 수 있습니다."
            ),
        )

    def test_failed_detail_request_preserves_previous_detail_results(self):
        successful_item = {"bidNtceNo": "FIRST-DETAIL"}
        successful_response = JsonResponse(
            {"response": {"body": {"items": [successful_item]}}}
        )
        original_numbers = api.bidNtceNos
        api.bidNtceNos = ["FIRST-DETAIL", "FAILED-DETAIL"]
        try:
            with patch(
                "api.requests.get",
                side_effect=[successful_response, requests.exceptions.Timeout(), requests.exceptions.Timeout(), requests.exceptions.Timeout()],
            ), patch("api.time.sleep"):
                items = api.get_data_w_number()
        finally:
            api.bidNtceNos = original_numbers

        self.assertEqual(items, [successful_item])
        self.assertEqual(
            api.get_scrape_errors()[-1],
            {
                "source": "나라장터 공고 상세정보 API",
                "message": "상세정보 전체 2건 중 1건을 수집하지 못해 일부 자료가 누락됐을 수 있습니다.",
            },
        )

    def test_all_failed_detail_requests_are_reported_as_full_failure(self):
        original_numbers = api.bidNtceNos
        api.bidNtceNos = ["FAILED-DETAIL-1", "FAILED-DETAIL-2"]
        try:
            with patch(
                "api.requests.get",
                side_effect=[requests.exceptions.Timeout()] * 6,
            ), patch("api.time.sleep"):
                items = api.get_data_w_number()
        finally:
            api.bidNtceNos = original_numbers

        self.assertEqual(items, [])
        messages = [error["message"] for error in api.get_scrape_errors()]
        self.assertIn(
            "상세정보 2건을 모두 수집하지 못했습니다. 이 항목은 0건이 아니라 수집 실패입니다.",
            messages,
        )

    def test_empty_response_body_is_reported_as_collection_failure(self):
        empty_response = type("Response", (), {"status_code": 200, "text": ""})()

        with patch("api.request_get_with_retry", return_value=empty_response):
            items = api.get_data_bid(api_url.URL_NEWOPEN_SERVICE, sign=False)

        self.assertIsNone(items)
        self.assertEqual(
            api.get_scrape_errors(),
            [
                {
                    "source": "나라장터 신규공고 용역 API",
                    "message": (
                        "API 응답 본문이 비어 있어 처리하지 못했습니다. "
                        "이 항목은 0건이 아니라 수집 실패입니다."
                    ),
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
